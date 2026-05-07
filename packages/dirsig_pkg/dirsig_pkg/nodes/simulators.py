
#---------------------------------------
# Copyright 2019-2025 DADoES, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the root directory in the "LICENSE" file or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#---------------------------------------

import logging
import anatools.lib.context as ctx
from anatools.lib.node import Node
import os
from glob import glob
from datetime import datetime, timedelta
import subprocess
import shutil
from pathlib import Path
import dirfm.atmosphere as atmos
from dirfm.ephemeris import EphemerisPlugin
from dirfm import TASKS
from dirfm.dirsig import DIRSIG
import dirfm.platform_sensor as ps
from dirfm.utilities.annotations import AnnotationsMetadata
from dirsig_pkg.lib.mask import mask_to_annotation
from spectral import open_image

logger = logging.getLogger(__name__)


class Simulate(Node):
    """A class to represent the DIRSIG Simulate Node."""

    def exec(self):
        logger.info("Executing {}".format(self.name))

        inPath = Path("/tmp/dirsig_input")
        outPath = Path("/tmp/dirsig_output")
        dirsig = DIRSIG(inPath, outPath)
        dirsig.set_seed(ctx.seed)

        # Register the scene object(s) with DIRSIG API. Tiled scenes pass a list
        # of sceneObjects with a parallel list of [x, y, z] meter offsets; the
        # legacy single-scene flow has offsets=None and we register one scene at
        # the origin.
        sceneBundle = self.inputs["Scene"][0]
        sceneObjects = sceneBundle["sceneObjects"]
        offsets = sceneBundle.get("offsets")
        if offsets is None:
            offsets = [[0, 0, 0]] * len(sceneObjects)
        for sceneObject, offset in zip(sceneObjects, offsets):
            dirsig.add_scene(sceneObject, offset=offset)

        # Resolve the platform sensor plugin from upstream nodes.
        platform_assets = self.inputs["Sensor"][0]
        platformObject = platform_assets["sensor"]

        #Add truth collection to the first focal plane of the first attached instrument
        firstInstrument = [i[0] for i in platformObject.get_instruments().values()][0]
        firstFocalPlane = firstInstrument.get_focalplanes()[0]
        if firstFocalPlane._truth_collection is None:
            captureBasename = firstFocalPlane.get_capture_filename().split('.')[0]
            firstFocalPlane.set_truth_collection(ps.TruthCollection(f"{captureBasename}-truth"))
        truthCollection = firstFocalPlane.get_truth_collection_names()
        
        if "Intersection" not in truthCollection:
            firstFocalPlane.add_truth_collection("Intersection")
        firstFocalPlane.add_truth_collection("material")
        firstFocalPlane.add_truth_collection("Abundance", tags=sceneBundle["tags"])

        motionObject = platform_assets["motion"]

        # Get reference time and build the task list.
        datetime_in = self.inputs["Reference Datetime"][0]
        if isinstance(datetime_in, datetime):
            ref_datetime = datetime_in
        else:
            try:
                ref_datetime = datetime.fromisoformat(datetime_in)
            except ValueError:
                logger.error(
                    "Input value 'datetime' must be in ISO 8601 format"
                )
                raise

        start_task_time = float(self.inputs["Start Task Time (s)"][0])
        capture_duration = float(self.inputs["Capture Duration (s)"][0])
        if ctx.preview:
            capture_duration = 0
        ref_datetime -= timedelta(hours=sceneBundle["timezone"])
        end_task_time = start_task_time + capture_duration
        logger.info(f"Creating task with reference {ref_datetime}, start time {start_task_time}s, end time {end_task_time}s, duration {capture_duration}s")
        tasks = TASKS(ref_datetime).add_start_stop(start_task_time, end_task_time)

        # New plugins API: motion and tasks live on the platform plugin itself,
        # and the platform is registered through dirsig.add_plugin.
        platformObject.set_motion(motionObject).set_tasks(tasks)
        dirsig.add_plugin(platformObject)

        ephemerisPlugin = self.inputs["Ephemeris"][0]

        # Register atmosphere first so that BasicAtmosphere's internal SpiceEphemeris
        # is installed before any FixedEphemeris plugin. FixedEphemeris must come last
        # in the JSIM plugin list so DIRSIG sets it up after SpiceEphemeris and it wins.
        atm = atmos.BasicAtmospherePlugin()
        atm.set_radiative_transfer(atmos.SimpleRadiativeTransfer(250))
        atm.set_weather(Path("$DIRSIG_HOME/lib/data/weather/jun2392.wth"))
        dirsig.add_plugin(atm)

        if isinstance(ephemerisPlugin, EphemerisPlugin):
            dirsig.add_plugin(ephemerisPlugin)

        # Collect scene metadata for the dataset annotations
        sceneMetadata = sceneBundle['metadata']
        sceneMetadata['capture_time'] = ref_datetime.isoformat()
    
        ephemerisData = {}
        if isinstance(ephemerisPlugin, EphemerisPlugin):
            ephemerisData['type'] = f"{ephemerisPlugin.get_plugin_name()}"
            ephemerisData['inputs'] = f"{ephemerisPlugin.get_plugin_inputs()}"
        else:
            ephemerisData['type'] = f"{ephemerisPlugin}"
            ephemerisData['inputs'] = None
        sceneMetadata['ephemeris'] = ephemerisData

        sceneMetadata['atmosphere'] = atm.get_metadata()

        # Run the simulation
        if "debug" in ctx.output:
            dirsig.run(log_level="debug", convergence="10,10,0", max_nodes="1")
        elif ctx.preview:
            dirsig.run(convergence="3,3,0", max_nodes="1")
        else:
            dirsig.run(convergence="20,100,1e-6", max_nodes="4") #default
            #dirsig.run(convergence="30,500,1e-6", max_nodes="5") #better

        #Process radiance measurements and collcted truth        
        for instruments in platformObject.get_instruments().values():
            for inst in instruments:
                for fp in inst.get_focalplanes():
                    #Get dirsig output files, these vary based on the platform's file scheduler
                    filebase = fp.get_capture_filename().split('.')[0]
                    truthFilename = fp.get_truth_filename()
                    if truthFilename is None:
                        truthfilebase = 'dummytruth'
                    else:
                        truthfilebase = truthFilename.split('.')[0]

                    #Get dirsig output files, these vary based on the platform's file scheduler
                    for dirsigout in glob(str(outPath) + '/' + filebase + '*'):
                        if truthfilebase in dirsigout or dirsigout.endswith('hdr'):
                            continue
                        enviFilePath = dirsigout
                        enviFileName = enviFilePath.split('/')[-1]

                        # Create an rgb image for the platform views
                        # http://dirsig.cis.rit.edu/docs/new/image_tool.html

                        rgbFileName = f"{enviFileName.split('.')[0]}.png"
                        rgbFilepath = os.path.join(ctx.output + "/images/" + rgbFileName)
                        if not os.path.isdir(ctx.output + "/images"):
                            os.mkdir(ctx.output + "/images")
                        subprocess.run(
                            ["image_tool", "convert"]
                            + platform_assets["convert_args"]
                            + ["--output=" + rgbFilepath, enviFilePath]
                        )

                        # Create a preview file, can use pillow to crop
                        if ctx.preview:
                            previewFilepath = os.path.join(ctx.output, "preview.png")
                            shutil.copy(rgbFilepath, previewFilepath)
                            return {}

                        if self.inputs['Save Radiance'][0] == "True":
                            os.makedirs(ctx.output + "/radiance", exist_ok=True)
                            shutil.copy(enviFilePath, ctx.output + "/radiance/" + enviFileName)
                            shutil.copy(enviFilePath + ".hdr", ctx.output + "/radiance/" + enviFileName + ".hdr")
                        
                        truthFilePath = dirsigout.replace(filebase, truthfilebase)
                        if os.path.exists(truthFilePath):
                            if self.inputs['Save ENVI Truth'][0]=="True":
                                os.makedirs(ctx.output + "/envi_truth", exist_ok=True)
                                shutil.copy(truthFilePath, ctx.output + "/envi_truth/" + truthFilePath.split('/')[-1])
                                shutil.copy(truthFilePath + ".hdr", ctx.output + "/envi_truth/" + truthFilePath.split('/')[-1] + ".hdr")
                            
                            anno = AnnotationsMetadata(rgbFileName, sceneMetadata=sceneMetadata)
                            
                            truthHeaderPath =  truthFilePath + ".hdr"
                        
                            img_data = open_image(truthHeaderPath)
                            bands = img_data.metadata["band names"]
                            for idx, band in enumerate(bands):
                                if "Abundance" not in band:
                                    continue
                                name = band.split("\'")[1]
                                objectType = "_".join([tok for tok in name.split("_") if not tok.isdigit()])
                                mask = img_data.read_band(idx)
                                annotation = mask_to_annotation(mask)
                                if not annotation.get("bbox"):
                                    continue

                                # Use the single bbox from mask_to_annotation for the entire mask
                                # Include all segments in the annotation if they exist
                                segments = annotation.get("segments", [])
                                if segments:
                                    # Use original bbox and include all segments
                                    entry = {
                                        "bbox": annotation["bbox"],
                                        "segmentation": annotation["segmentation"],
                                        "segmentation_fill": annotation["segmentation_fill"],
                                        "segments": segments
                                    }
                                    anno.add_entry(name=name, type=objectType, **entry)
                                else:
                                    # Single-object case without segments
                                    anno.add_entry(name=name, type=objectType, **annotation)

                            anno_dir = Path(ctx.output) / "annotations"
                            meta_dir = Path(ctx.output) / "metadata"
                            if not anno_dir.exists():
                                os.makedirs(anno_dir)
                            if not meta_dir.exists():
                                os.makedirs(meta_dir)
                            anno.write(
                                anno_dir / f"{enviFileName.split('.')[0]}-ana.json",
                                meta_dir / f"{enviFileName.split('.')[0]}-metadata.json",
                            )

        return {}
