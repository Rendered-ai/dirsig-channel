
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
import numpy as np
import json
import os

PACKAGE_ROOT = os.path.join('packages', 'dirsig_pkg', 'dirsig_pkg')

def instrument(instrument_name, focal_length, focal_plane=None, aperture_diameter=None, aperture_throughput=None):
    """Creates a DIRSIG generic instrument with specified optical properties.

    Args:
        instrument_name (str): The name of the instrument.
        focal_length (float): The focal length of the instrument.
        focal_plane (dirfm.platform_sensor.FocalPlane, optional): A focal plane to add to the instrument. Defaults to None.
        aperture_diameter (float, optional): The diameter of the aperture. Defaults to None.
        aperture_throughput (float, optional): The throughput of the aperture [0-1]. Defaults to None.

    Returns:
        A configured dirfm instrument.
    """
    
    instrument = ps.GenericInstrument(instrument_name)
    instrument.add_property(
        ps.FocalLengthInstrumentProperty(focal_length, aperture_diameter=aperture_diameter, aperture_throughput=aperture_throughput)
        )
    if focal_plane is not None:
        instrument.add_focal_plane(focal_plane)
    
    return instrument


def detector_array(resolution=(1024, 1280), pixel_pitch=5, detector_clock_rate=0.9, offset=(0,0), flip=(False, True)):
    """Creates a DIRSIG detector array.

    Args:
        resolution (tuple, optional): The (width, height) of the array in pixels. Defaults to (1024, 1280).
        pixel_pitch (float, optional): The size of each pixel in microns. Defaults to 5.
        detector_clock_rate (float, optional): The clock rate of the detector in Hz. Defaults to 0.9.
        offset (tuple, optional): The offset of the detector array in microns. Defaults to (0,0).
        flip (tuple, optional): The flip axis of the detector array. Defaults to (False, True).

    Returns:
        A configured dirfm detector array.
    """
    detectorArray = ps.DetectorArray("microns")
    detectorArray.set_clock(ps.IndependentDetectorClock(detector_clock_rate, 0))
    detectorArray.set_elements(resolution[0], resolution[1], pixel_pitch, pixel_pitch, pixel_pitch, pixel_pitch, offset[0], offset[1], flip[0], flip[1])
    return detectorArray


def focal_plane(band_name, image_file, spectral_response,
                int_time=None, psf=None, dirfm_detector_array=None):
    """Creates a DIRSIG focal plane with a capture method and detector array.

    Args:
        band_name (str): The name of the focal plane assembly (e.g., "Red FPA").
        image_file (dirfm.platform_sensor.ImageFile): The image file object for output.
        spectral_response (dirfm.platform_sensor.SpectralResponse): The spectral response for this focal plane.
        int_time (float, optional): The integration time. Defaults to None.
        psf (dirfm.platform_sensor.PSF, optional): The point spread function. Defaults to None.
        dirfm_detector_array (dirfm.platform_sensor.DetectorArray, optional): A pre-configured detector array. 
            If None, a default one is created. Defaults to None.

    Returns:
        A configured dirfm focal plane.
    """
    
    # Create a capture method
    captureMethod = ps.BasicCaptureMethod("Simple")
    captureMethod.set_image_file(image_file)
    captureMethod.set_spectral_response(spectral_response)
    if int_time is not None:
        captureMethod.set_temporal_integration(time=int_time, samples=10)
    if psf is not None:
        captureMethod.set_psf(psf)        

    # Build out the focal plane
    focalPlane = ps.FocalPlane(band_name + " FPA")
    focalPlane.set_capture_method(captureMethod)
    
    # Add a detector array
    if dirfm_detector_array is None:
        dirfm_detector_array = detector_array()
    focalPlane.set_detector_array(dirfm_detector_array)
    
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
    sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)

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
    sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)

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
    sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)

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
    sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)

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
    sensor = ps.PlatformSensorPlugin().add_attachment(mountAttachment)

    return sensor


def thermal_sensor(integration_time=None, band_limits=[8, 14], focal_length=1142, resolution=(400, 260), pixel_pitch=8, truth_bands=[], schedule="simulation", detector_clock_rate=25, psf=None):
    sensorName="Thermal"
    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName.replace(' ', '_'))
    truthCollection = ps.TruthCollection(f"{imgbasename}-truth")
    for truthCollectorName in truth_bands:
        truthCollection.add_collection(truthCollectorName)

    imageFile = ps.ImageFile(imgbasename, schedule=schedule)

    spectralResponse = ps.SpectralResponse()
    spectralResponse.set_band("microns", band_limits[0], band_limits[1], step=0.01)
    spectralResponse.add_channel(ps.FunctionalChannel("Channel", float(np.mean(band_limits)), float(np.diff(band_limits))))
  
    detectorArray = detector_array(resolution=resolution, pixel_pitch=pixel_pitch, detector_clock_rate=detector_clock_rate)
    thermalFocalPlane = focal_plane("ThermalBand", imageFile, spectralResponse, int_time=integration_time, dirfm_detector_array=detectorArray, psf=psf)
    thermalFocalPlane.set_truth_collection(truthCollection)
    
    instrument = ps.GenericInstrument(sensorName)
    instrument.add_property(ps.FocalLengthInstrumentProperty(focal_length, units="mm"))
    instrument.add_focal_plane(thermalFocalPlane)
    
    return instrument


def altumPT_sensor(resolution=(2064, 1544), truth_bands=[], rgb_only=False, use_real_integration_times=False, detector_clock_rate=30, schedule="simulation", add_pan=False, override_focal_length=None, mount_orientation="Down", pan_only=False, sensor_name=None):
    sensorName = sensor_name if sensor_name else "AltumPT"
    datatype = 4

    imgbasename = '{:010}-{}'.format(ctx.interp_num, sensorName)
    truthCollection = None
    if truth_bands:
        truthCollectionName = f"{imgbasename}_Green-truth"
        if pan_only:
            truthCollectionName = f"{imgbasename}-truth"
        truthCollection = ps.TruthCollection(truthCollectionName)
        for truthCollectorName in truth_bands:
            truthCollection.add_collection(truthCollectorName)

    # Define band properties
    band_definitions = {
        "Blue": {"center": 0.475, "width": 0.032},
        "Green": {"center": 0.560, "width": 0.027},
        "Red": {"center": 0.668, "width": 0.016},
        "Red Edge": {"center": 0.717, "width": 0.012},
        "NIR": {"center": 0.842, "width": 0.057},
        "Pan": {"center": 0.6345, "width": 0.463}
    }

    msi_spectral_response = None
    if not pan_only:
        if rgb_only:
            inst = ps.GenericInstrument(sensorName + "_RGB")
        else:
            inst = ps.GenericInstrument(sensorName + "_MSI")
        msi_spectral_response = ps.SpectralResponse()
        min_wl = band_definitions['Blue']['center'] - band_definitions['Blue']['width']/2
        max_wl = band_definitions['NIR']['center'] + band_definitions['NIR']['width']/2
        num_samples = 500
        step = (max_wl - min_wl) / num_samples
        msi_spectral_response.set_band("microns", min_wl, max_wl, step=step)

        msi_bands_to_add = ["Blue", "Green", "Red", "Red Edge", "NIR"]
        if rgb_only or ctx.preview:
            msi_bands_to_add = ["Blue", "Green", "Red"]

        for band_name in msi_bands_to_add:
            band = band_definitions[band_name]
            msi_spectral_response.add_channel(ps.FunctionalChannel(band_name, band['center'], band['width']))

    # Create PAN spectral response
    pan_band = band_definitions['Pan']
    pan_spectral_response = ps.SpectralResponse()
    min_wl_pan = pan_band['center'] - pan_band['width']/2
    max_wl_pan = pan_band['center'] + pan_band['width']/2
    pan_step = (max_wl_pan - min_wl_pan) / 100 # Use 100 samples for PAN band
    pan_spectral_response.set_band("microns", min_wl_pan, max_wl_pan, step=pan_step)
    pan_spectral_response.add_channel(ps.FunctionalChannel('Pan', pan_band['center'], pan_band['width']))

    msi_focal_plane = None
    if not pan_only:
        msi_img_basename = f"{imgbasename}_MSI"
        msi_img_file = ps.ImageFile(msi_img_basename, schedule=schedule)
        msi_detector = detector_array(resolution=resolution, pixel_pitch=3.45, detector_clock_rate=detector_clock_rate)
        msi_focal_plane = focal_plane("MSI", msi_img_file, msi_spectral_response, dirfm_detector_array=msi_detector)
        if truthCollection:
            msi_focal_plane.set_truth_collection(truthCollection)

    # Create PAN focal plane
    pan_img_basename = imgbasename if pan_only else f"{imgbasename}_PAN"
    pan_img_file = ps.ImageFile(pan_img_basename, schedule=schedule)
    # PAN resolution is 2x MSI when used alongside MSI, otherwise use resolution directly
    pan_resolution = resolution if pan_only else (resolution[0]*2, resolution[1]*2)
    pan_detector = detector_array(resolution=pan_resolution, pixel_pitch=3.45, detector_clock_rate=detector_clock_rate)
    pan_focal_plane = focal_plane("PAN", pan_img_file, pan_spectral_response, dirfm_detector_array=pan_detector)

    if pan_only:
        if truthCollection:
            pan_focal_plane.set_truth_collection(truthCollection)
        if override_focal_length is not None:
            pan_focal_length = float(override_focal_length)
        else:
            pan_focal_length = 8.2
    else:
        if override_focal_length is not None:
            msi_focal_length = float(override_focal_length)
            pan_focal_length = float(override_focal_length) * 2.0
        else:
            msi_focal_length = 8.0
            pan_focal_length = 16.4

        inst.add_property(ps.FocalLengthInstrumentProperty(msi_focal_length, units="mm", aperture_diameter=1.8))
        inst.add_focal_plane(msi_focal_plane)

    # Create the PAN instrument
    panInstrument = ps.GenericInstrument(sensorName + " PAN")
    panInstrument.add_property(ps.FocalLengthInstrumentProperty(pan_focal_length, units="mm", aperture_diameter=4.5))
    panInstrument.add_focal_plane(pan_focal_plane)

    # Determine mount rotation based on orientation
    if mount_orientation == "Forward":
        mount_rotation = (90, 0, 0)
    else:  # Default "Down" orientation
        mount_rotation = (0, 0, 0)

    # Create the sensor and mount with the MSI and PAN instruments
    sensor = ps.PlatformSensorPlugin()
    mountAttachment = ps.Attachment(ps.StaticMount("Mount").set_rotation("xyz", "degrees", mount_rotation[0], mount_rotation[1], mount_rotation[2]))
    if pan_only:
        mountAttachment.add_attachment(ps.Attachment(panInstrument))
    else:
        mountAttachment.add_attachment(ps.Attachment(inst))
        if not rgb_only and add_pan:
            mountAttachment.add_attachment(ps.Attachment(panInstrument))
    sensor.add_attachment(mountAttachment)

    return sensor
