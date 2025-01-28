
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

from dirfm import platform_sensor as ps
from pathlib import Path
import anatools.lib.context as ctx
import pdb
import json
import os


PACKAGE_ROOT = os.path.join('packages', 'dirsig_pkg', 'dirsig_pkg')

def instrument(instrument_name, focal_length, focal_plane, aperture_diameter=None, aperture_throughput=None):
    
    instrument = ps.GenericInstrument(instrument_name)
    instrument.add_property(
        ps.FocalLengthInstrumentProperty(focal_length, aperture_diameter=aperture_diameter, aperture_throughput=aperture_throughput)
        )
    instrument.add_focal_plane(focal_plane)
    
    return instrument


def focal_plane(band_name, image_file, spectral_response):
    captureMethod = ps.BasicCaptureMethod("Simple")
    captureMethod.set_image_file(image_file)
    captureMethod.set_spectral_response(spectral_response)
    # captureMethod.set_temporal_integration(time=int_time, samples=10)
    # captureMethod.set_detector_model(
    #         quantum_efficiency=quantum_efficiency,
    #         read_noise=read_noise,
    #         max_electrons=max_electrons,
    #         dark_current_density=dark_current_density,
    #         bit_depth=12,
    #         )
    # if psf is not None:
    #     captureMethod.set_psf(psf)
    focalPlane = ps.FocalPlane(band_name + " FPA")
    focalPlane.set_capture_method(captureMethod)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(0.9, 0))
        .set_elements(1024, 1280, 5, 5, 5, 5, 0, 0, False, True)
        )
    
    return focalPlane


def tabulated_spectral_response(platformFilepath):
    """Create a spectral response that has tabulated throughput
    """
    #Specify spectral response
    
    with open(platformFilepath) as fin:
        srData = json.load(fin)
    
    sr = ps.SpectralResponse()
    sr.set_band(srData['bandpass']['spectralunits'], srData['bandpass']['minimum'], srData['bandpass']['maximum'], step=srData['bandpass']['delta'])
    for chnl in srData['channellist']:
        sr.add_channel(
            ps.TabulatedChannel(
                chnl["name"],
                chnl['spectralpoints'],
                chnl['values'],
            )
        )

    return sr


def functional_spectral_response(platformFilepath):
    """Create a spectral response that has tabulated throughput
    """
    #Specify spectral response
    
    with open(platformFilepath) as fin:
        srData = json.load(fin)
    
    sr = ps.SpectralResponse()
    sr.set_band(srData['bandpass']['spectralunits'], srData['bandpass']['minimum'], srData['bandpass']['maximum'], step=srData['bandpass']['delta'])
    for chnl in srData['channellist']:
        sr.add_channel(
            ps.FunctionalChannel(
                chnl["name"],
                chnl['center'],
                chnl['width'],
                func_type=chnl['shape'],
            )
        )

    return sr


def rgb_camera(
        focal_length=35,
        rotation=(0,0,0), rot_order="xyz",rot_units='degrees',
        truth_bands=["Intersection"],
        schedule="simulation", detector_clock_rate=30
    ):
    sensorName = "RGB Camera"

    #Spectral Response
    platformFilepath = Path(PACKAGE_ROOT) / "platform" / "rgb_camera_spectralresponse.json"
    spectralResponse = tabulated_spectral_response(platformFilepath)

    #Focal plane
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))  
    imgFile = ps.ImageFile(imgbasename, schedule=schedule)
    focalPlane = focal_plane(sensorName, imgFile, spectralResponse)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
        .set_elements(1280, 720, 10, 10, 10, 10, 0, 0, False, True)
        )
    
    #Set truth bands
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth", schedule=schedule)
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)
    focalPlane.set_truth_collection(truthCollection)

    # Sensor
    rgbInstrument = instrument(sensorName, focal_length=35, focal_plane=focalPlane)

    staticMount = ps.StaticMount("Static Mount")
    staticMount.set_rotation(
        order=rot_order,
        units=rot_units,
        x=rotation[0],
        y=rotation[1],
        z=rotation[2],
    )
    mountAttachment = ps.Attachment(staticMount)
    mountAttachment.add_attachment(ps.Attachment(rgbInstrument))
    sensor = ps.PlatformSensor().add_attachment(mountAttachment)

    return sensor


def wv3_sensor(truth_bands=[], schedule="simulation", detector_clock_rate=30):
    sensorName = "WV3"

    #Spectral Response
    platformFilepath = Path(PACKAGE_ROOT) / "platform" / "wv3_640x480_spectralresponse.json"
    spectralResponse = tabulated_spectral_response(platformFilepath)
    
    #Focal plane
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))  
    imgFile = ps.ImageFile(imgbasename, schedule=schedule)
    focalPlane = focal_plane(sensorName, imgFile, spectralResponse)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
        .set_elements(640, 480, 20, 20, 20, 20, 0, 0, False, True)
        )
    
    #Set truth bands
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth", schedule=schedule)
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)
    focalPlane.set_truth_collection(truthCollection)
    
    # Sensor
    wv3Instrument = instrument(sensorName, focal_length=10000, focal_plane=focalPlane)

    mountAttachment = ps.Attachment(ps.StaticMount("Static Mount"))
    mountAttachment.add_attachment(ps.Attachment(wv3Instrument))
    sensor = ps.PlatformSensor().add_attachment(mountAttachment)

    return sensor


def skysat_sensor(truth_bands=[], schedule="simulation", detector_clock_rate=30):
    sensorName = "SkySat"
    
    #Spectral Response
    platformFilepath = Path(PACKAGE_ROOT) / "platform" / "planet_skysat_1024x768_spectralresponse.json"
    spectralResponse = tabulated_spectral_response(platformFilepath)

    #Focal plane
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))  
    imgFile = ps.ImageFile(imgbasename, schedule=schedule)
    focalPlane = focal_plane(sensorName, imgFile, spectralResponse)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
        .set_elements(1024, 768, 6.5, 6.5, 6.5, 6.5, 0, 0, False, True)
        )
    
    #Set truth bands
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth", schedule=schedule)
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)
    focalPlane.set_truth_collection(truthCollection)
    
    # Sensor
    skysatInstrument = instrument(sensorName, focal_length=3600, aperture_diameter=0.35, aperture_throughput=1, focal_plane=focalPlane)

    mountAttachment = ps.Attachment(ps.StaticMount("Static Mount"))
    mountAttachment.add_attachment(ps.Attachment(skysatInstrument))
    sensor = ps.PlatformSensor().add_attachment(mountAttachment)

    return sensor


def superdove_sensor(truth_bands=[], schedule="simulation", detector_clock_rate=30):
    sensorName = "SuperDove"

    #Spectral Response
    platformFilepath = Path(PACKAGE_ROOT) / "platform" / "planet_superdove_640x480_spectralresponse.json"
    spectralResponse = tabulated_spectral_response(platformFilepath)

    #Focal plane
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))  
    imgFile = ps.ImageFile(imgbasename, schedule=schedule)
    focalPlane = focal_plane(sensorName, imgFile, spectralResponse)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
        .set_elements(640, 480, 8.0, 8.0, 8.0, 8.0, 0, 0, False, True)
        )
    
    #Set truth bands
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth", schedule=schedule)
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)
    focalPlane.set_truth_collection(truthCollection)
    
    # Sensor
    superdoveInstrument = instrument(sensorName, focal_length=1140, aperture_diameter=0.09, aperture_throughput=1, focal_plane=focalPlane)

    mountAttachment = ps.Attachment(ps.StaticMount("Static Mount"))
    mountAttachment.add_attachment(ps.Attachment(superdoveInstrument))
    sensor = ps.PlatformSensor().add_attachment(mountAttachment)

    return sensor


def aviris_sensor(truth_bands=[], schedule="simulation", detector_clock_rate=1000):
    sensorName = "AVIRIS"
    
    #Spectral Response
    platformFilepath = Path(PACKAGE_ROOT) / "platform" / "aviris_spectralresponse.json"
    spectralResponse = functional_spectral_response(platformFilepath)
    
    #Focal plane
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))  
    imgFile = ps.ImageFile(imgbasename, schedule=schedule)
    focalPlane = focal_plane(sensorName, imgFile, spectralResponse)
    focalPlane.set_detector_array(
        ps.DetectorArray("microns")
        .set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
        .set_elements(667, 512, 200, 200, 200, 200, 0, 0, False, False)
        )
    
    #Set truth bands
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth")
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)
    focalPlane.set_truth_collection(truthCollection)
    
    # Sensor
    avirisInstrument = instrument(sensorName, focal_length=197.6, aperture_diameter=0.2, focal_plane=focalPlane)

    mountAttachment = ps.Attachment(ps.StaticMount("Static Mount"))
    mountAttachment.add_attachment(ps.Attachment(avirisInstrument))
    sensor = ps.PlatformSensor().add_attachment(mountAttachment)

    return sensor