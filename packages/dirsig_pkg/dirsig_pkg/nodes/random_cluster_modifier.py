
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
# This module contains an object modifier node that creates clusters of AnaDirsigObject instances.
# The RandomClusterObjects node creates an ObjectModifier generator with a custom set_static_instances function.
# This demonstrates the plugin pattern where the modifier function is assigned to generator.function
# rather than requiring a method on the AnaDirsigObject class.

import logging
from anatools.lib.node import Node
from anatools.lib.generator import ObjectModifier
from dirsig_pkg.lib.object import AnaDirsigObject, file_to_objgen
from dirsig_pkg.lib.utils import array_input
from dirsig_pkg.lib.spatial_sampling_utils import random_points_in_polygon, hexagon
import anatools.lib.context as ctx
from dirfm import glist

logger = logging.getLogger(__name__)

def set_static_instances(ana_object, locations, tags=[]):
    """ Create a a batch of static instances for an object
    Inputs:
        ana_object: The object to create instances for
        locations: A list of locations to create instances at
        tags: A list of tags to apply to the instances. Labels that control object behavior in simulations.
            An example use of an instance tag is to enable LightCurve tracking: https://dirsig.cis.rit.edu/docs/new/lightcurve_plugin.html
    """
    # Remove any existing instances
    ana_object.root._instance = []

    # Create a static instance for each location
    for idx, loc in enumerate(locations):
        instance = glist.StaticInstance(name=f"{ana_object.name}_{str(idx).zfill(4)}", translation=loc, rotation=[0, 0, ctx.random.random() * 360])
        for tag in tags:
            instance.set_tag(tag)
        ana_object.root.add_instance(instance)
    
    # Collect metadata
    ana_object.modifiers.append({
        "RandomCluster_N": {
            "Number of Objects": len(locations)
        }
    })


class ClusterObjects(Node):
    """ A class to represent the ClusterObjects node
        - Places objects at random locations within a hexagonal area with random rotations
        - Generated locations have zero elevation (z=0), requiring terrain alignment afterward
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
    
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        n_objects = int(self.inputs["Number of Objects"][0])
        center = array_input(self.inputs['Scene Location (m, m)'][0])
        radius = int(self.inputs["Radius (m)"][0])

        poly = hexagon(center, radius)
        xy_locations = random_points_in_polygon(poly, n_objects)

        # Add modifier to the generator tree
        generator = ObjectModifier(
            method="set_static_instances",
            children=children,
            locations=xy_locations,
            # tags = self.inputs["Tags"][0],
        )

        # Assign the modifier function to the generator
        generator.function = set_static_instances

        return {'Objects': generator}
