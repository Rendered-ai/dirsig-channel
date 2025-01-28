
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

from lxml.etree import parse
import pdb

def spectralresponse(focalplane_element):
    """ Extract the spectralresponse from a DIRSIG focal plane xml element. Retrun metadata and a list of python dictionaries for each channel.
    Example spectral response element:
            <spectralresponse>
                <bandpass spectralunits="microns">
                  <minimum>0.44</minimum>
                  <maximum>0.92</maximum>
                  <delta>0.001</delta>
                </bandpass>
                <channellist>
                  <channel shape="tabulated" gain="1" bias="0" name="Blue" normalize="true">
                    <entry>
                      <spectralpoint>0.44</spectralpoint>
                      <value>0.001</value>
                    </entry>
                    ...
    Or 
                <channellist>
                  <channel shape="gaussian" bias="0" name="Channel #1" gain="1" normalize="true">
                    <center>0.3734</center>
                    <width>0.0099</width>
                    <polarizer type="none"/>
                    <dataoutput type="total"/>
                  </channel>
                  ...
    """
    
    spectralResponseEl = focalplane_element.find('.//spectralresponse')
    
    #Create a serializable python dictionary and add the bandpass data
    spectralResponse = {}
    bandpassEl = spectralResponseEl.find("bandpass")
    spectralResponse['bandpass'] = {k:v for k,v in bandpassEl.items()}
    spectralResponse['bandpass']['minimum'] = float(bandpassEl.find("minimum").text)
    spectralResponse['bandpass']['maximum'] = float(bandpassEl.find("maximum").text)
    spectralResponse['bandpass']['delta'] = float(bandpassEl.find("delta").text)

    #Collect the channel list
    channel_list = []
    for chan in spectralResponseEl.findall('.//channel'):
        chan_serializable = {k:v for k,v in chan.items()}
        if chan_serializable['shape']=="tabulated":
            chan_serializable['spectralpoints'] = []
            chan_serializable['values'] = []
            for entry in chan.findall('entry'):
                chan_serializable['spectralpoints'].append(float(entry.find('spectralpoint').text))
                chan_serializable['values'].append(float(entry.find('value').text))
            
        elif chan_serializable['shape']=="gaussian":
            
            chan_serializable['center'] = float(chan.find('center').text)
            chan_serializable['width'] = float(chan.find('width').text)
            # chan_serializable['].append(float(chan.find('polarizer')))
            # chan_serializable[''].append(float(chan.find('dataoutput')))

        channel_list.append(chan_serializable)
    #Add the channels to the spectral response dictionary and return it
    spectralResponse['channellist'] = channel_list

    return spectralResponse


if __name__ == "__main__":
    import os
    TEMPLATES_ROOT = os.path.join('packages', 'dirsig', 'dirsig')
    
    #platformFilename = "wv3_640x480"
    #platformFilename = "planet_skysat_1024x768"
    #platformFilename = "planet_superdove_640x480"
    #platformFilename = "rgb_35mm"
    platformFilename = "aviris"
    platformFilepath = os.path.join(TEMPLATES_ROOT, f"platform/{platformFilename}.platform")

    platformTree = parse(platformFilepath)
    pElement = platformTree.getroot()
    focalplaneEl = pElement.findall(".//focalplane")[0] # All these platforms have a single focal plane
    in_sr = spectralresponse(focalplaneEl)

    import json
    with open(os.path.join(TEMPLATES_ROOT, f"platform/{platformFilename}_spectralresponse.json"), 'w') as fout:
        json.dump(in_sr, fout)
    