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
# This module contains an object modifier node that applies scale transformations to AnaDirsigObject instances.
# The ScaleObjects node creates an ObjectModifier generator with a custom scale_modifier function.
# This demonstrates the plugin pattern where the modifier function is assigned to generator.function
# rather than relying on a method that must exist on the AnaDirsigObject class.

import logging
from anatools.lib.node import Node
from anatools.lib.generator import ObjectModifier
from dirsig_pkg.lib.utils import array_input

logger = logging.getLogger(__name__)

def scale_modifier(ana_object, scale_factors):
    """ AnaObject plugin - Adjust the scale of an object """
    # Update the scale factors if all this glist object's instances by the input array of 3 floats
    for objInstance in ana_object.root.get_instances():
        objInstance.set_scale([objInstance.get_scale()[i]*scale_factors[i] for i in range(3)])
        
        # Collect metadata
        ana_object.modifiers.append({
            "Scale_N": {
                "Scale Factors": scale_factors
            }
        })


class ScaleObjects(Node):
    """ Adjust the scale of an object """

    def exec(self):
        children = self.inputs["Objects"]
        scale_factors = array_input(self.inputs["Scale Factors"][0])

        # Add modifier to the generator tree
        generator = ObjectModifier(
            method="scale_plugin",
            children=children,
            scale_factors=scale_factors)
        
        # Assign the modifier function to the generator
        generator.function = scale_modifier

        return {"Objects": generator}
