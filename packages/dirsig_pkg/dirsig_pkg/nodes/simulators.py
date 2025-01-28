
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
from dirfm.utilities.annotations import AnnotationsMetadata
from dirsig_pkg.lib.mask import create_mask
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

        # Register the scene object with DIRSIG API
        sceneBundle = self.inputs["Scene"][0]
        sceneObjects = sceneBundle["sceneObjects"]
        dirsig.set_scene(sceneObjects[0])

        # Register the platform, motion, and tasks with DIRSIG API
        platform_assets = self.inputs["Sensor"][0]
        platformObject = platform_assets["sensor"]

        #Add truth collection to the first focal plane of the first attached instrument
        firstInstrument = [i[0] for i in platformObject.get_instruments().values()][0]
        firstFocalPlane = firstInstrument.get_focalplanes()[0]
        firstFocalPlane.add_truth_collection("Intersection")
        firstFocalPlane.add_truth_collection("Abundance", tags=sceneBundle["tags"])

        dirsig.set_platform(platformObject)

        motionObject = platform_assets["motion"]
        dirsig.set_motion(motionObject)

        # Get reference time and create task list
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

        capture_duration = float(self.inputs["Capture Duration (s)"][0])
        if ctx.preview:
            capture_duration = 0
        ref_datetime -= timedelta(hours=sceneBundle["timezone"])
        logger.info(f"Creating task with reference {ref_datetime} and duration {capture_duration}")
        tasks = TASKS(ref_datetime).add_start_stop(0, capture_duration)
        dirsig.set_tasks(tasks)

        ephemerisPlugin = self.inputs["Ephemeris"][0]
        if isinstance(ephemerisPlugin, EphemerisPlugin):
            dirsig.set_ephemeris(ephemerisPlugin)

        atm = atmos.BasicAtmosphere()
        atm.set_radiative_transfer(atmos.SimpleRadiativeTransfer(250))
        atm.set_weather(Path("$DIRSIG_HOME/lib/data/weather/jun2392.wth"))
        dirsig.set_atmosphere(atm)

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
                    truthfilebase = fp.get_truth_filename().split('.')[0]
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
                                            
                        truthFilePath = dirsigout.replace(filebase, truthfilebase)
                        if os.path.exists(truthFilePath):
                            sceneMetadata = sceneBundle['metadata']
                            anno = AnnotationsMetadata(rgbFileName, sceneMetadata=sceneMetadata)
                            
                            truthHeaderPath =  truthFilePath + ".hdr"
                        
                            img_data = open_image(truthHeaderPath)
                            bands = img_data.metadata["band names"]
                            for idx, band in enumerate(bands):
                                if "Abundance" not in band:
                                    continue
                                try:
                                    name = band.split("\'")[1]
                                    t = name.split("_")[0]
                                    mask = create_mask(img_data.read_band(idx))
                                    anno.add_entry(name=band.split("\'")[1],type=t, **mask)
                                except:
                                    logger.info("File [{}] contains band [{}] that couldn't be masked".format(Path(img_data.filename).name,band))

                            anno_dir = Path(ctx.output) / "annotations"
                            meta_dir = Path(ctx.output) / "metadata"
                            if not anno_dir.exists():
                                os.makedirs(anno_dir)
                            if not meta_dir.exists():
                                os.makedirs(meta_dir)
                            anno.write(
                                anno_dir / f"{enviFileName.split('.')[0]}-annotations.json",
                                meta_dir / f"{enviFileName.split('.')[0]}-metadata.json",
                            )

        return {}
