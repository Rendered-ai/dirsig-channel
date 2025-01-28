
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
from re import T
import anatools.lib.context as ctx
from anatools.lib.node import Node
import os
from datetime import datetime
from dirsig_pkg.lib.camera import *
from dirfm.input_fmt import fmt_VecNum
import dirfm.platform_sensor as ps

logger = logging.getLogger(__name__)

TEMPLATES_ROOT = os.path.join('packages', 'dirsig', 'dirsig')


class WorldView3(Node):
    """ A class to represent the WorldView 3 sensor node.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        
        # Get the spectrometer (DIRSIG platform), optionally add truth collectors
        truthBands = []
        if self.inputs['Collect Geolocation'][0] == "T":
            truthBands.append("GeoLocation")
        if self.inputs['Collect Intersection'][0] == "T":
            truthBands.append("Intersection")
        
        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"

        platformSensorObject = wv3_sensor(truth_bands=truthBands, schedule=schedule, detector_clock_rate=detectorClockRate)
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': platformSensorObject,
            'motion': motion,
            'convert_args': ["--bands=2,3,4", "--percent=0", "--per_band"],
        }
        return {"Sensor": sensorAssets}


class SkySat(Node):
    """ A class to represent the SkySat sensor node.
    """
    
    def exec(self):
        logger.info("Executing {}".format(self.name))
        
        # Get the spectrometer (DIRSIG platform), optionally add truth collectors
        truthBands = []
        if self.inputs['Collect Geolocation'][0] == "T":
            truthBands.append("GeoLocation")
        if self.inputs['Collect Intersection'][0] == "T":
            truthBands.append("Intersection")
        
        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
        
        platformSensorObject = skysat_sensor(truth_bands=truthBands, schedule=schedule, detector_clock_rate=detectorClockRate)

        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': platformSensorObject,
            'motion': motion,
            'convert_args': ["--bands=2,1,0", "--sigma=2"]
        }
        return {"Sensor": sensorAssets}


class SuperDove(Node):
    """ A class to represent the SuperDove sensor node.
    """
    
    def exec(self):
        logger.info("Executing {}".format(self.name))
        
        # Get the spectrometer (DIRSIG platform), optinally add truth collectors
        truthBands = []
        if self.inputs['Collect Geolocation'][0] == "T":
            truthBands.append("Geolocation")
        if self.inputs['Collect Intersection'][0] == "T":
            truthBands.append("Intersection")
        if self.inputs['Collect Shadow'][0] == "T":
            truthBands.append("Shadow")

        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
        
        # Create the platform bundle
        platformSensorObject = superdove_sensor(truth_bands=truthBands, schedule=schedule, detector_clock_rate=detectorClockRate)
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': platformSensorObject,
            'motion': motion,
            'convert_args': ["--bands=5, 3, 1", "--percent=0", "--per_band"],
        }
        return {"Sensor": sensorAssets}


class Drone(Node):
    """ A class to represent the Drone sensor node.
    """
    
    def exec(self):
        logger.info("Executing {}".format(self.name))

        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
        
        # Create the platform bundle
        platforSensorObject = rgb_camera(
            focal_length=35,
            truth_bands=[],
            schedule=schedule, detector_clock_rate=detectorClockRate,
        )
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': platforSensorObject,
            'motion': motion,
            'convert_args': ["--bands=0, 1, 2", "--percent=2"],
        }
        return {"Sensor": sensorAssets}


class SatelliteHSI(Node):
    """ A class to represent the Satellite HSI sensor node.
    """
    
    def exec(self):
        logger.info("Executing {}".format(self.name))

        # Get the spectrometer (DIRSIG platform), optionally add truth collectors
        truthBands = []
        if self.inputs['Collect Material'][0] == "T":
            truthBands.append("Material")
        if self.inputs['Collect Intersection'][0] == "T":
            truthBands.append("Intersection")
        if self.inputs['Collect Shadow'][0] == "T":
            truthBands.append("Shadow")
        
        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"

        # Get spectrometer the altitude and create the platform bundle
        platformSensorObject = aviris_sensor(truth_bands=[], schedule=schedule, detector_clock_rate=detectorClockRate)
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': platformSensorObject,
            'motion': motion,
            'convert_args': ["--band=10", "--percent=0"],
        }
        return {"Sensor": sensorAssets}


class CustomRGBSensor(Node):
    """ A class to represent the Custom RGB sensor node.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        pixels = fmt_VecNum(self.inputs["Pixels"][0])
        pitch = fmt_VecNum(self.inputs["Pixel Pitch"][0])
        focal_length = float(self.inputs["Focal Length"][0])

        sensor = ps.PlatformSensor().add_attachment(
            ps.Attachment(
                ps.StaticMount("Mount").set_rotation(
                    "xyz", "degrees", 0, 0, 0
                )
            ).add_attachment(
                ps.Attachment(
                    ps.GenericInstrument("Custom")
                    .add_property(
                        ps.FocalLengthInstrumentProperty(
                            focal_length, units="mm"
                        )
                    )
                    .add_focal_plane(
                        ps.FocalPlane("FocalPlane")
                        .set_capture_method(
                            ps.BasicCaptureMethod("Simple")
                            .set_image_file(
                                ps.ImageFile("{:010d}-{}".format(ctx.interp_num,"CustomRGB"))
                            )
                            .set_temporal_integration(0, 10)
                            .set_spectral_response(
                                ps.SpectralResponse()
                                .set_band(
                                    "microns",
                                    0.4,
                                    0.7,
                                    step=0.01,
                                )
                                .add_channel(
                                    ps.FunctionalChannel(
                                        "Red",
                                        0.65,
                                        0.1,
                                    )
                                )
                                .add_channel(
                                    ps.FunctionalChannel(
                                        "Green",
                                        0.55,
                                        0.1,
                                    )
                                )
                                .add_channel(
                                    ps.FunctionalChannel(
                                        "Blue",
                                        0.45,
                                        0.1,
                                    )
                                )
                            )
                        )
                        .set_detector_array(
                            ps.DetectorArray("microns")
                            .set_clock(ps.IndependentDetectorClock(1000.0, 0))
                            .set_elements(
                                pixels[0],
                                pixels[1],
                                pitch[0],
                                pitch[1],
                                pitch[0],
                                pitch[1],
                                0,
                                0,
                                False,
                                True,
                            )
                        ).set_truth_collection(ps.TruthCollection("{:010d}-{}".format(ctx.interp_num,"CustomRGBTruth")))
                    )
                )
            )
        )
            
        # Get spectrometer the altitude and create the platform bundle
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': sensor,
            'motion': motion,
            'convert_args': ["--bands=0, 1, 2", "--percent=2"],
        }
        return {"Sensor": sensorAssets}

