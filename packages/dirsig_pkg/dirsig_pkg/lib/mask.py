
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
from scipy import ndimage
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
  segments = []  # list of per-component polygons (flattened)
  
  # Find all non-zero points in the mask
  non_zero_points = np.argwhere(img > 0.0)
  
  # Only process if we have points to work with
  if len(non_zero_points) > 0:
    # Convert to x,y format (swap columns for ConvexHull)
    points = np.array([[y, x] for x, y in non_zero_points])
    
    # ConvexHull requires at least 3 points and non-collinear points
    hull_vertices = None
    if len(points) >= 3:
      # Check if points are collinear by examining coordinate ranges
      x_range = np.max(points[:, 0]) - np.min(points[:, 0])
      y_range = np.max(points[:, 1]) - np.min(points[:, 1])
      
      # If one dimension has zero range, points are collinear
      if x_range > 0 and y_range > 0:
        try:
          # Calculate convex hull
          hull = ConvexHull(points)
          hull_vertices = points[hull.vertices]
          
          # Extract bounding box coordinates from hull vertices
          min_x = int(np.min(hull_vertices[:, 0]))
          max_x = int(np.max(hull_vertices[:, 0]))
          min_y = int(np.min(hull_vertices[:, 1]))
          max_y = int(np.max(hull_vertices[:, 1]))
        except Exception as e:
          logger.warning(f"ConvexHull failed, falling back to bbox only: {e}")
          # Fallback to simple bounding box if ConvexHull fails
          min_x = int(np.min(points[:, 0]))
          max_x = int(np.max(points[:, 0]))
          min_y = int(np.min(points[:, 1]))
          max_y = int(np.max(points[:, 1]))
      else:
        # Points are collinear, use simple bounding box
        min_x = int(np.min(points[:, 0]))
        max_x = int(np.max(points[:, 0]))
        min_y = int(np.min(points[:, 1]))
        max_y = int(np.max(points[:, 1]))
    else:
      # For cases with fewer than 3 points, use all points for bounding box
      min_x = int(np.min(points[:, 0]))
      max_x = int(np.max(points[:, 0]))
      min_y = int(np.min(points[:, 1]))
      max_y = int(np.max(points[:, 1]))
    
    # Format as [x, y, width, height]
    bbox = [min_x, min_y, max_x - min_x, max_y - min_y]
    
    # Build a simple, non-self-intersecting polygon for the segmentation.
    # Prefer the convex hull (ordered) when available; otherwise use the bbox rectangle.
    if hull_vertices is not None and len(hull_vertices) >= 3:
      # ConvexHull vertices are returned in counter-clockwise order and form a simple polygon.
      for vx, vy in hull_vertices:
        segmentation.extend([int(vx), int(vy)])
      # Use the same clean boundary for segmentation_fill to avoid criss-cross artifacts in viewers.
      segmentation_fill = segmentation.copy()
    else:
      # Fallback polygon: rectangle from bounding box
      rect = [
        (min_x, min_y),
        (max_x, min_y),
        (max_x, max_y),
        (min_x, max_y),
      ]
      for vx, vy in rect:
        segmentation.extend([int(vx), int(vy)])
      segmentation_fill = segmentation.copy()

    # Additionally, split into connected components so thin parallel objects (e.g., multiple cables)
    # can be represented as multiple simple polygons instead of one merged mask.
    try:
      labeled, nlab = ndimage.label(img > 0.0)
      for lab in range(1, nlab+1):
        pts_idx = np.argwhere(labeled == lab)
        if len(pts_idx) < 3:
          continue
        pts = np.array([[y, x] for x, y in pts_idx])
        xr = np.max(pts[:,0]) - np.min(pts[:,0])
        yr = np.max(pts[:,1]) - np.min(pts[:,1])
        poly_flat = []
        if xr > 0 and yr > 0:
          try:
            h = ConvexHull(pts)
            for vx, vy in pts[h.vertices]:
              poly_flat.extend([int(vx), int(vy)])
          except Exception:
            # fallback to small rectangle bbox
            mnx, mxx = int(np.min(pts[:,0])), int(np.max(pts[:,0]))
            mny, mxy = int(np.min(pts[:,1])), int(np.max(pts[:,1]))
            rect2 = [(mnx,mny),(mxx,mny),(mxx,mxy),(mnx,mxy)]
            for vx, vy in rect2:
              poly_flat.extend([int(vx), int(vy)])
        else:
          mnx, mxx = int(np.min(pts[:,0])), int(np.max(pts[:,0]))
          mny, mxy = int(np.min(pts[:,1])), int(np.max(pts[:,1]))
          rect2 = [(mnx,mny),(mxx,mny),(mxx,mxy),(mnx,mxy)]
          for vx, vy in rect2:
            poly_flat.extend([int(vx), int(vy)])
        if poly_flat:
          segments.append(poly_flat)
    except Exception as e:
      logger.warning(f"Connected component split failed: {e}")
  
  # Return annotation dictionary
  return {
    "bbox": bbox,
    "segmentation": segmentation,
    "segmentation_fill": segmentation_fill,
    "segments": segments,
  }
