
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
from pathlib import Path
import numpy as np
from dirsig_pkg.lib.cluster import Cluster
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon
from anatools.lib.generator import Generator, CreateBranchGenerator
from dirfm.utilities.grid_position_generator import grid_position_generator
import anatools.lib.context as ctx

logger = logging.getLogger(__name__)

class GridClusterGenerator(Generator):
    """ Random Cluster Generator """

    def exec(self, *args, **kwargs):

        create_object = CreateBranchGenerator(self.children)
        instances = self.kwargs["object_instances"]
        # put everything in the same cluster
        cluster = Cluster("random")
        
        for instance in range(instances):
            # create an object
            obj = create_object.exec()
            
            # pick a random point inside the polygon
            locations = grid_position_generator(dims, spacing, rotation, deviation, seed=ctx.random.randint(0,1e6))
            
            
            cluster.objects.append(obj)

        return cluster