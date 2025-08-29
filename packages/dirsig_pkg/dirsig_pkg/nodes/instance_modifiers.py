
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

# Instance Modifiers Summary:
# This module contains nodes that modify object instances by leveraging existing methods on the AnaDirsigObject class.
# Unlike the plugin pattern (where custom functions are assigned to generator.function),
# these modifiers reference methods that must already exist on the AnaDirsigObject class.
# - PoseObjects: Applies translation and rotation to objects, with options for terrain matching
# - DynamizeObjects: Converts static objects to dynamic objects with motion paths

import logging
from anatools.lib.node import Node
from anatools.lib.generator import ObjectModifier
from dirsig_pkg.lib.object import AnaDirsigObject, file_to_objgen
from dirsig_pkg.lib.utils import array_input

logger = logging.getLogger(__name__)


class PoseObjects(Node):
    """ A class to represent the PoseObjects node
    """

    def exec(self):
        # Collect inputs
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        transVec = array_input(self.inputs["Translation (m)"][0])
        rotFac = array_input(self.inputs["Rotation (deg)"][0])
        matchSlope = self.inputs["Match Slope"][0]
        matchElevation = self.inputs["Match Elevation"][0]
        
        # Add modifier to the generator tree
        generator = ObjectModifier(
            method="move",
            children=children,
            trans_vector=transVec,
            rot_vector=rotFac,
            match_slope = matchSlope=="True",
            match_elevation = matchElevation=="True",
        )
        return {"Objects": generator}


class DynamizeObjects(Node):
    """ A class to represent the DynamizeObjects node
    """

    def exec(self):
        # Collect inputs
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        m = self.inputs["Flex Motion"][0]
        
        # Add modifier to the generator tree
        generator = ObjectModifier(
            method="set_dynamic_instance",
            children=children,
            motion=m,
        )
        return {"Objects": generator}
