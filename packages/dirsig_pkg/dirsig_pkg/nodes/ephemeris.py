
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

import pdb
from pathlib import Path
import logging
from anatools.lib.node import Node
from dirfm.ephemeris import SimpleSolarEphemerisPlugin, FixedEphemerisPlugin, SPICEPlugin

logger = logging.getLogger(__name__)


class FixedEphemerisNode(Node):
    """ A class to repreesent the Fixed Ephemeris node 
    """
    def exec(self):
        logger.info("Executing {}".format(self.name))

        solarZenith = float(self.inputs['Solar Zenith'][0])
        solarAzimuth = float(self.inputs['Solar Azimuth'][0])
        lunarZenith = float(self.inputs['Lunar Zenith'][0])
        lunarAzimuth = float(self.inputs['Lunar Azimuth'][0])
        lunarFraction = float(self.inputs['Lunar Fraction'][0])
        plugin = FixedEphemerisPlugin(
                solar_zenith=solarZenith,
                solar_azimuth=solarAzimuth,
                lunar_zenith=lunarZenith,
                lunar_azimuth=lunarAzimuth,
                lunar_fraction=lunarFraction,
        )
        return {"Ephemeris": plugin}