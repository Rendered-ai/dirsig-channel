
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

# Spatial sampling uility functions for generating and manipulating spatial distributions.
# These utilities support object placement in scenes with controlled randomness.

import logging
from pathlib import Path
import numpy as np
from dirfm import glist
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon
from shapely.ops import triangulate
import anatools.lib.context as ctx
from scipy.spatial import distance

logger = logging.getLogger(__name__)

def random_points_in_polygon(polygon, k):
    """
    Return list of k points in 2 dimensions chosen uniformly at random inside the polygon.
    Source: https://codereview.stackexchange.com/questions/69833/generate-sample-coordinates-inside-a-polygon
    """
    areas = []
    transforms = []
    for t in triangulate(polygon):
        areas.append(t.area)
        (x0, y0), (x1, y1), (x2, y2), _ = t.exterior.coords
        transforms.append([x1 - x0, x2 - x0, y2 - y0, y1 - y0, x0, y0])
    points = []
    # ctx.random is a numpy RandomState seeded by the run, so this is
    # deterministic per (seed, interp_num). See agent-docs/AGENT.md.
    probabilities = np.array(areas) / np.sum(areas)
    chosen_indices = ctx.random.choice(len(transforms), size=k, p=probabilities)
    for idx in chosen_indices:
        transform = transforms[idx]
        x, y = [ctx.random.random() for _ in range(2)]
        if x + y > 1:
            p = Point(1 - x, 1 - y)
        else:
            p = Point(x, y)
        points.append(affine_transform(p, transform))
    locations = [[point.x, point.y, 0.0] for point in points]
    return locations

def random_points_in_polygon_with_min_distance(polygon, k, min_dist, max_attempts=1000):
    """
    Return list of k points in 2 dimensions chosen uniformly at random inside the polygon,
    with a minimum distance between points.
    """
    points = []
    attempts = 0
    while len(points) < k and attempts < max_attempts:
        # Generate a single random point
        new_point_list = random_points_in_polygon(polygon, 1)
        if not new_point_list:
            attempts += 1
            continue

        new_point = new_point_list[0]
        
        # Check distance to existing points
        is_valid = True
        for existing_point in points:
            if distance.euclidean(new_point, existing_point) < min_dist:
                is_valid = False
                break
        
        if is_valid:
            points.append(new_point)
            attempts = 0 # Reset attempts after a successful placement
        else:
            attempts += 1

    if len(points) < k:
        logger.warning(f"Could only place {len(points)} out of {k} requested points with minimum distance {min_dist}.")

    return points


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
