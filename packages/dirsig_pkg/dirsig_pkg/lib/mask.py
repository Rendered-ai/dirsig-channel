
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

from scipy.spatial import ConvexHull
import numpy as np

logger=logging.getLogger(__name__)

def create_mask(img):
  """
  Creates "bbox" and "segmentation" values for annotations.

  img must have the shape of the original image and only contain one
  object to segment whose pixels are greater than 0.0
  """

  points = list()
  for x in range(img.shape[0]):
    for y in range(img.shape[1]):
      if img[x,y] > 0.0:
        points.append([x,y])

  points = np.array(points)
  hull = ConvexHull(points)

  min_x = int(min(points[hull.vertices,1]))
  max_x = int(max(points[hull.vertices,1]))
  min_y = int(min(points[hull.vertices,0]))
  max_y = int(max(points[hull.vertices,0]))
  segmentation = list()
  for vert in hull.vertices:
    segmentation.append(int(points[vert,1]))
    segmentation.append(int(points[vert,0]))
  segmentation_fill = list()
  for p in points:
    segmentation_fill.append(int(p[1]))
    segmentation_fill.append(int(p[0]))
  return {"bbox":[min_x,min_y,max_x-min_x,max_y-min_y],
          "segmentation": segmentation,
          "segmentation_fill":segmentation_fill
          }
