
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
from anatools.lib.node import Node
from anatools.lib.generator import ObjectModifier
from dirsig_pkg.lib.object import AnaDirsigObject, file_to_objgen
from dirsig_pkg.lib.cluster_generator_random import RandomClusterGenerator
from dirsig_pkg.lib.utils import array_input

logger = logging.getLogger(__name__)


class ScaleObjects(Node):
    """ A class to represent the ScaleObjects node
    """

    def exec(self):
        # takes one or more object generators as input
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        scaleFac = array_input(self.inputs["Scale Factors"][0])

        # add modifier to the generator tree
        generator = ObjectModifier(
            method="scale",
            children=children,
            scale_factors=scaleFac)
        return {"Objects": generator}


class PoseObjects(Node):
    """ A class to represent the PoseObjects node
    """

    def exec(self):
        # takes one or more object generators as input
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        transVec = array_input(self.inputs["Translation (m)"][0])
        rotFac = array_input(self.inputs["Rotation (deg)"][0])
        matchSlope = self.inputs["Match Slope"][0]
        
        # add modifier to the generator tree
        generator = ObjectModifier(
            method="move",
            children=children,
            trans_vector=transVec,
            rot_vector=rotFac,
            match_slope = matchSlope=="True",
        )
        return {"Objects": generator}


class DynamizeObjects(Node):
    """ A class to represent the DynamizeObjects node
    """

    def exec(self):
        # takes one or more object generators as input
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        m = self.inputs["Flex Motion"][0]
        
        # add modifier to the generator tree
        generator = ObjectModifier(
            method="set_dynamic_instance",
            children=children,
            motion=m,
        )
        return {"Objects": generator}


class ClusterObjects(Node):
    """ A class to represent the ClusterObjects node
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
    
        children = file_to_objgen(self.inputs["Objects"], AnaDirsigObject)
        n_objects = int(self.inputs["Number of Objects"][0])
        location = array_input(self.inputs['Scene Location (m, m)'][0])
        radius = int(self.inputs["Radius (m)"][0])

        generator = RandomClusterGenerator(
            children=children,
            n_objects=n_objects,
            center=location,
            radius=radius,
        )

        return {'Objects': generator}
