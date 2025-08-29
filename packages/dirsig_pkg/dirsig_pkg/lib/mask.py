
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

def mask_to_annotation(img):
  """
  Converts a binary mask image to annotation format with bounding box and segmentation data.
  
  Parameters:
  -----------
  img : numpy.ndarray
      2D array representing a binary mask where values > 0.0 indicate the object to segment.
      Must contain only one object.
      
  Returns:
  --------
  dict
      Dictionary containing:
      - 'bbox': [x, y, width, height] format bounding box
      - 'segmentation': List of x,y coordinates of the convex hull vertices (flattened)
      - 'segmentation_fill': List of x,y coordinates of all points in the mask (flattened)
  """
  # Initialize empty containers
  bbox = []
  segmentation = []
  segmentation_fill = []
  
  # Find all non-zero points in the mask
  non_zero_points = np.argwhere(img > 0.0)
  
  # Only process if we have points to work with
  if len(non_zero_points) > 0:
    # Convert to x,y format (swap columns for ConvexHull)
    points = np.array([[y, x] for x, y in non_zero_points])
    
    # Calculate convex hull
    hull = ConvexHull(points)
    
    # Extract bounding box coordinates
    min_x = int(np.min(points[hull.vertices, 0]))
    max_x = int(np.max(points[hull.vertices, 0]))
    min_y = int(np.min(points[hull.vertices, 1]))
    max_y = int(np.max(points[hull.vertices, 1]))
    
    # Format as [x, y, width, height]
    bbox = [min_x, min_y, max_x - min_x, max_y - min_y]
    
    # Extract segmentation points from hull vertices (flattened x,y pairs)
    # for vertex in hull.vertices:
    #   segmentation.append(int(points[vertex, 0]))  # x coordinate
    #   segmentation.append(int(points[vertex, 1]))  # y coordinate
    
    # Include all points for segmentation_fill (flattened x,y pairs)
    for point in points:
      segmentation_fill.append(int(point[0]))  # x coordinate
      segmentation_fill.append(int(point[1]))  # y coordinate
  
  # Return annotation dictionary
  return {
    "bbox": bbox,
    "segmentation": segmentation,
    "segmentation_fill": segmentation_fill,
  }
