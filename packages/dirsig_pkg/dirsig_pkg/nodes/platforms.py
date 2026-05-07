
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

        # Parse truth bands from comma-separated list
        truthBands = [band.strip() for band in self.inputs["Truth Bands"][0].split(',') if band.strip()]
        
        pixels = fmt_VecNum(self.inputs["Pixels"][0])
        pitch = fmt_VecNum(self.inputs["Pixel Pitch"][0])
        focal_length = float(self.inputs["Focal Length"][0])
        detectorClockRate = float(self.inputs['Detector Clock Rate (Hz)'][0])
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
            
        # Get mount orientation parameter
        mount_orientation = self.inputs.get('Mount Orientation', ['Down'])[0]
            
        # Create a truth collection object with schedule parameter
        truthCollection = ps.TruthCollection("{:010d}-{}".format(ctx.interp_num,"CustomRGBTruth"), schedule=schedule)
        
        # Add each specified truth band to the collection
        for truth_band in truthBands:
            truthCollection.add_collection(truth_band)

        # Determine mount rotation based on orientation
        if mount_orientation == "Forward":
            mount_rotation = (90, 0, 0)
        else:  # Default "Down" orientation
            mount_rotation = (0, 0, 0)

        sensor = ps.PlatformSensorPlugin().add_attachment(
            ps.Attachment(
                ps.StaticMount("Mount").set_rotation(
                    "xyz", "degrees", mount_rotation[0], mount_rotation[1], mount_rotation[2]
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
                                ps.ImageFile("{:010d}-{}".format(ctx.interp_num,"CustomRGB"), schedule=schedule)
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
                                        func_type="wymanx",
                                    )
                                )
                                .add_channel(
                                    ps.FunctionalChannel(
                                        "Green",
                                        0.55,
                                        0.1,
                                        func_type="wymany",
                                    )
                                )
                                .add_channel(
                                    ps.FunctionalChannel(
                                        "Blue",
                                        0.45,
                                        0.1,
                                        func_type="wymanz",
                                    )
                                )
                            )
                        )
                        .set_detector_array(
                            ps.DetectorArray("microns")
                            .set_clock(ps.IndependentDetectorClock(detectorClockRate, 0))
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
                        ).set_truth_collection(truthCollection)
                    )
                )
            )
        )
            
        # Get spectrometer the altitude and create the platform bundle
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': sensor,
            'motion': motion,
            'convert_args': ["--bands=0,1,2", "--percent=2", "--xyztorgb", "--tonemap=srgb"],
        }
        return {"Sensor": sensorAssets}


class ThermalSensor(Node):
    """ A class to represent the Thermal sensor node."""
    
    def exec(self):
        logger.info("Executing {}".format(self.name))
        
        # Get the band limits
        band_limits = fmt_VecNum(self.inputs['Band Limits'][0])

        # Get the sensor properties
        pixels = fmt_VecNum(self.inputs["Pixels"][0])
        pitch = fmt_VecNum(self.inputs["Pixel Pitch"][0])
        focal_length = float(self.inputs["Focal Length"][0])
        
        # Get the spectrometer (DIRSIG platform), optionally add truth collectors
        truthBands = []
        if self.inputs['Collect Location'][0] == "T":
            truthBands.append("GeoLocation")
            truthBands.append("Intersection")
        if self.inputs['Collect Material'][0] == "T":
            truthBands.append("Material")
        if self.inputs['Collect Temperature'][0] == "T":
            truthBands.append("Temperature")
        
        
        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]
        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
    
        # Get PSF from node input
        input_psf=int(self.inputs['MTF PSF Blur (pixels)'][0])
        psf = ps.GaussianPSF(width=input_psf)

        # Get shutter speed from node input
        integration_time = float(self.inputs['Shutter Speed (s)'][0])
        
        # Get mount orientation parameter
        mount_orientation = self.inputs.get('Mount Orientation', ['Down'])[0]
        
        instrument = thermal_sensor(
            band_limits=band_limits,
            resolution=pixels,
            pixel_pitch=pitch,
            focal_length=focal_length,
            truth_bands=truthBands,
            schedule=schedule,
            detector_clock_rate=detectorClockRate,
            psf=psf,
            integration_time=integration_time,
        )
        
        # Determine mount rotation based on orientation
        if mount_orientation == "Forward":
            mount_rotation = (90, 0, 0)
        else:  # Default "Down" orientation
            mount_rotation = (0, 0, 0)
            
        mountAttachment = ps.Attachment(ps.StaticMount("Static Mount").set_rotation("xyz", "degrees", mount_rotation[0], mount_rotation[1], mount_rotation[2]))
        mountAttachment.add_attachment(ps.Attachment(instrument))
        sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)
    
        motion = self.inputs['Flex Motion'][0]
        sensorAssets = {
            'sensor': sensor,
            'motion': motion,
            'convert_args': [],
        }
        return {"Sensor": sensorAssets}

    
class AltumPT(Node):

    def exec(self):
        logger.info("Executing {}".format(self.name))

        resolution = fmt_VecNum(self.inputs["Resolution"][0])

        rgb_only = self.inputs["RGB Only"][0]=='True'

        add_pan = self.inputs["Add PAN"][0]=='True'

        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]

        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"
        
        # Get override focal length parameter - use None if set to default 0.0
        override_focal_length = None
        if 'Override Focal Length (mm)' in self.inputs:
            focal_value = float(self.inputs['Override Focal Length (mm)'][0])
            if focal_value != 0.0:  # 0.0 means use defaults
                override_focal_length = focal_value

        # Get mount orientation parameter
        mount_orientation = self.inputs.get('Mount Orientation', ['Down'])[0]

        truthBands = []
        truthBands.append("Intersection")
        sensor = altumPT_sensor(
            resolution=resolution, 
            truth_bands=truthBands, 
            rgb_only=rgb_only,
            add_pan=add_pan,
            use_real_integration_times=True,
            detector_clock_rate=detectorClockRate, 
            schedule=schedule,
            override_focal_length=override_focal_length,
            mount_orientation=mount_orientation,
        )

        motion = self.inputs['Flex Motion'][0]
        
        sensorAssets = {
            'sensor': sensor,
            'motion': motion,
            'convert_args': ["--band=2"],
        }
        return {"Sensor": sensorAssets}


class ElectroOptical(Node):

    def exec(self):
        logger.info("Executing {}".format(self.name))

        resolution = fmt_VecNum(self.inputs["Resolution"][0])

        detectorClockRate = self.inputs['Detector Clock Rate (Hz)'][0]

        schedule = self.inputs['File Schedule'][0]
        if ctx.preview:
            schedule = "simulation"

        override_focal_length = None
        if 'Override Focal Length (mm)' in self.inputs:
            focal_value = float(self.inputs['Override Focal Length (mm)'][0])
            if focal_value != 0.0:
                override_focal_length = focal_value

        mount_orientation = self.inputs.get('Mount Orientation', ['Down'])[0]

        truthBands = []
        collect_truth = self.inputs.get('Collect Truth', ['True'])[0] == 'True'
        if collect_truth:
            truthBands.append("Intersection")
        sensor = altumPT_sensor(
            resolution=resolution,
            truth_bands=truthBands,
            rgb_only=False,
            add_pan=True,
            pan_only=True,
            use_real_integration_times=True,
            detector_clock_rate=detectorClockRate,
            schedule=schedule,
            override_focal_length=override_focal_length,
            mount_orientation=mount_orientation,
            sensor_name="EO",
        )

        motion = self.inputs['Flex Motion'][0]

        sensorAssets = {
            'sensor': sensor,
            'motion': motion,
            'convert_args': ["--band=0"],
        }
        return {"Sensor": sensorAssets}