
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
import logging
from pathlib import Path
import numpy as np
from dirsig_pkg.lib.cluster import Cluster
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon
from shapely.ops import triangulate
from anatools.lib.generator import Generator, CreateBranchGenerator
import anatools.lib.context as ctx
import random

logger = logging.getLogger(__name__)

def random_points_in_polygon(polygon, k):
    """
    Return list of k points chosen uniformly at random inside the polygon.
    Source: https://codereview.stackexchange.com/questions/69833/generate-sample-coordinates-inside-a-polygon
    """
    areas = []
    transforms = []
    for t in triangulate(polygon):
        areas.append(t.area)
        (x0, y0), (x1, y1), (x2, y2), _ = t.exterior.coords
        transforms.append([x1 - x0, x2 - x0, y2 - y0, y1 - y0, x0, y0])
    points = []
    # TODO: This is not repeatable. Need to create a ctx equivalent of random.choices
    for transform in random.choices(transforms, weights=areas, k=k):
        x, y = [ctx.random.random() for _ in range(2)]
        if x + y > 1:
            p = Point(1 - x, 1 - y)
        else:
            p = Point(x, y)
        points.append(affine_transform(p, transform))
    locations = [[point.x, point.y, 0.0] for point in points]
    return locations


def hexagon(location=(0,0), radius=1):
    """ Generate the verticies of the hexagon about a given coordinate pair. """
    center = Point(location)
    vertices = []
    for i in range(6):
        angle = 2 * np.pi * i / 6
        x = center.x + radius * np.cos(angle)
        y = center.y + radius * np.sin(angle)
        vertices.append((x, y))

    return Polygon(vertices)


class RandomClusterGenerator(Generator):
    """ Random Cluster Generator """

    def exec(self):

        # create an object
        child = self.select_child()
        anaObject = child.exec()

        #Add a cluster to the object
        center = self.kwargs.get("center", (0,0))
        radius = self.kwargs.get("radius", 1.0)
        n_objects = self.kwargs.get("n_objects", 1)
        poly = hexagon(center, radius)
        locations = random_points_in_polygon(poly, n_objects)
        
        #Create a cluster 
        cluster = Cluster("Random Cluster", locations)

        #Setting static binary instance
        anaObject.set_binfile_instance(cluster.locations_filepath)
        anaObject.root.set_tag(anaObject.name)

        return anaObject