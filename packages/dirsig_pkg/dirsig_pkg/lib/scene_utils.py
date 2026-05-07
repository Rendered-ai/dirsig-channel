
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
import subprocess
import os
import json
import re
import hashlib
import tempfile
import numpy as np
from scipy.spatial.transform import Rotation
from pathlib import Path
from dirfm.scene import SCENE
from dirfm import glist, materials,frames

DIRS={
    'root': Path("/tmp/elevation"),
    'maps': Path("/tmp/elevation/maps"),
    'material': Path("/tmp/elevation/materials"),
    'geometry': Path("/tmp/elevation/geometry"),
}
for d in DIRS.values():
    if not os.path.isdir(str(d)):
        os.mkdir(str(d))


# Pattern for splitting multi-curve <beziercurveset> blocks. The bundled
# LWIR_Urban_Alt power_line.glist asset stores 3 cubic Bezier curves per
# <beziercurveset> with a single <matid>, which DIRSIG treats as a
# materialData array of size 1 even though it produces 3 primitives.
# Shadow rays striking the 2nd or 3rd curve then trip
# 'Out of range object material requested!'
# (size_t(ray.primID) >= obj->materialData.size()) and abort the run.
# patch_glist_split_beziercurvesets() rewrites such files so each
# <beziercurveset> contains exactly one curve with its own <matid>.
_BEZIER_CURVESET_RE = re.compile(
    r'<beziercurveset>\s*<vertexdata>(.*?)</vertexdata>\s*'
    r'<firstindexes>([^<]+)</firstindexes>\s*'
    r'<matid>([^<]+)</matid>\s*</beziercurveset>',
    re.DOTALL,
)


def _split_beziercurveset(match):
    """Replace a multi-curve <beziercurveset> with one set per curve.

    Vertex data is a flat sequence of 4-tuples (x, y, z, radius). Curves
    are cubic Beziers with 4 control points each, and <firstindexes> lists
    the start index of every curve in the shared vertex array. Adjacent
    curves share an endpoint, so curve i spans verts[start_i : start_{i+1}+1]
    (the last curve runs to the end of the vertex array).
    """
    verts_text = match.group(1)
    fi_text = match.group(2).strip()
    matid_text = match.group(3).strip()
    starts = fi_text.split()
    if len(starts) <= 1:
        return match.group(0)
    nums = verts_text.split()
    # Each control point is 4 floats (x y z radius); refuse to touch malformed data.
    if len(nums) % 4 != 0:
        return match.group(0)
    n_verts = len(nums) // 4
    starts_i = [int(s) for s in starts]
    chunks = []
    for i, s in enumerate(starts_i):
        e = starts_i[i + 1] + 1 if i + 1 < len(starts_i) else n_verts
        curve_nums = nums[s * 4 : e * 4]
        chunks.append(
            '<beziercurveset>\n'
            '<vertexdata>{}</vertexdata>\n'
            '<firstindexes>0</firstindexes>\n'
            '<matid>{}</matid>\n'
            '</beziercurveset>'.format(' '.join(curve_nums), matid_text)
        )
    return '\n'.join(chunks)


def patch_glist_split_beziercurvesets(source_path):
    """Return a glist Path with single-curve <beziercurveset> blocks.

    If the source already contains only single-curve sets the original path
    is returned untouched. Otherwise a patched copy is cached under
    /tmp/dirsig_pkg_patched/ keyed by source path + mtime + size, and that
    cached path is returned. Subsequent calls with an unchanged source reuse
    the cached file.
    """
    source_path = Path(source_path)
    src = source_path.read_text()
    # Fast bail-out: only rewrite if at least one set has multiple curves.
    if not any(
        len(m.group(2).split()) > 1 for m in _BEZIER_CURVESET_RE.finditer(src)
    ):
        return source_path

    stat = source_path.stat()
    key_seed = "{}|{}|{}".format(source_path, stat.st_mtime_ns, stat.st_size)
    digest = hashlib.sha1(key_seed.encode()).hexdigest()[:12]
    cache_dir = Path(tempfile.gettempdir()) / "dirsig_pkg_patched"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / "{}_{}.glist".format(source_path.stem, digest)
    if not out_path.exists():
        patched = _BEZIER_CURVESET_RE.sub(_split_beziercurveset, src)
        out_path.write_text(patched)
    return out_path


def terrain_scene(terrain_bundle_object):
        """Compile a one-object elevation scene to HDF for height/normal lookups.

        The input is expected to be a glist.Object wrapping an *elevation
        scene glist* — a single-object glist whose base geometry is a terrain
        heightmap (e.g. ``<scene>/geometry/terrain_elevation.glist`` shipped
        alongside each scene's bundle). The result is a compiled ``.scene.hdf``
        path suitable for passing to :func:`elevation`.
        """
        sceneName="Elevation"
        sceneObj = SCENE(sceneName).set_properties("vis")
        dummyMat = materials.Material("Dummy", ID="999999")
        dummyMat.add_surface_properties(materials.WardBrdfSurfaceProperty([1,1],[1,1]))
        #dummyMat.set_temp_solver(materials.DataDrivenTempSolver(100))
        sceneObj.add_material(dummyMat)

        sceneObj.set_ems_dir(DIRS["material"])
        sceneObj.set_ext_dir(DIRS["material"])
        sceneObj.set_abs_dir(DIRS["material"])
        sceneObj.set_src_dir(DIRS["material"])
        sceneObj.set_map_dir(DIRS["maps"])
        
        terrain_bundle_object.add_instance(glist.StaticInstance("terrain"))
        sceneGlist =  glist.GLIST().add_object(terrain_bundle_object)
        sceneObj.add_geometry("Elevation", sceneGlist)
        sceneObj.set_origin(frames.GeodeticFrame(0,0,0))

        sceneFilepath = str(sceneObj.write(DIRS, out_fname="elevation.scene"))
        
        result1 = subprocess.run(
            ["scene2hdf", sceneFilepath],
            capture_output=True,
            text=True,
            env=os.environ,
        )
        print(result1.stderr)
        return sceneFilepath + ".hdf"


def elevation(scene_hdf_path, location_x, location_y):
    """Look up terrain height and surface normal at an (x, y) ENU location.

    Performs a downward raycast from above the scene's bounding box max-Z
    onto the compiled elevation scene HDF produced by :func:`terrain_scene`.

    Args:
        scene_hdf_path: Path to the compiled ``.scene.hdf`` from
            ``terrain_scene()``, which itself was built from an elevation
            scene glist (see :func:`terrain_scene`).
        location_x: ENU x coordinate in meters.
        location_y: ENU y coordinate in meters.

    Returns:
        tuple ``(height_m, surface_normal_xyz)`` where ``height_m`` is the
        terrain height at (x, y) and ``surface_normal_xyz`` is a 3-element
        list giving the unit surface normal at the hit point.

    Raises:
        RuntimeError: if the raycast finds no terrain at (x, y), typically
            because the location lies outside the terrain bounds.
    """
    result = subprocess.run(
        ["scene_tool", "summary", scene_hdf_path],
        capture_output=True,
        text=True,
        env=os.environ,
    )
    data0 = json.loads(result.stdout)
    originAlt = str(
        int(data0[scene_hdf_path]['boxMax'][2]) + 1
    )

    def _raycast_z(x, y):
        out = subprocess.run(
            ["scene_tool", "raycast", "--origin", str(x), str(y), originAlt, "--direction", "0", "0", "-1", scene_hdf_path],
            capture_output=True,
            text=True,
            env=os.environ,
        )
        hits = json.loads(out.stdout)
        if not hits:
            return None
        return hits[0]['hitPosition'][2]

    locationZ = _raycast_z(location_x, location_y)
    if locationZ is None:
        raise RuntimeError(
            f"Terrain raycast failed at coordinates ({location_x}, {location_y}). "
            f"No terrain geometry found at this location. "
            f"This may indicate that the object is positioned outside the terrain bounds "
            f"or the terrain geometry is missing from the scene."
        )

    # The new scene_tool raycast no longer reports a hit normal, so derive it
    # from a forward-difference over two neighbouring samples. Falls back to
    # straight-up [0, 0, 1] if either neighbour misses the terrain.
    eps = 1.0
    zx = _raycast_z(location_x + eps, location_y)
    zy = _raycast_z(location_x, location_y + eps)
    if zx is None or zy is None:
        surfaceNormal = [0.0, 0.0, 1.0]
    else:
        nx, ny, nz = -(zx - locationZ) / eps, -(zy - locationZ) / eps, 1.0
        norm = (nx * nx + ny * ny + nz * nz) ** 0.5
        surfaceNormal = [nx / norm, ny / norm, nz / norm]

    return locationZ, surfaceNormal


def align_directions(target_direction, source_direction, units="radians"):
    """ Convert a surface normal vector to a set of euler angles to align an input vector
    Input target_direction, source_direction - vectors: tuples of 3 floats
    Output a list of 3 Euler angles in radians
    """
    surfaceNormal = np.array(target_direction)
    objNormal = np.array(source_direction)

    # surfaceNormal = np.array([1,0,1])
    # surfaceNormal = surfaceNormal / np.linalg.norm(surfaceNormal)
    
    rotationAxis = np.cross(objNormal, surfaceNormal)
    axisNorm = np.linalg.norm(rotationAxis)
    if axisNorm < 1e-9:
        # Vectors are parallel (or antiparallel). For our terrain alignment
        # use case the parallel case is the only realistic one, so a zero
        # rotation is the correct answer.
        eulerAngles = np.array([0.0, 0.0, 0.0])
    else:
        rotationAngle = np.arccos(np.clip(np.dot(objNormal, surfaceNormal), -1.0, 1.0))
        rotation = Rotation.from_rotvec(rotationAxis / axisNorm * rotationAngle)
        eulerAngles = rotation.as_euler('xyz') #radians
    if units == "degrees":
         eulerAngles = [a*180/np.pi for a in eulerAngles]

    return eulerAngles

    
if __name__ == "__main__":

    # Example: see terrain_scene/elevation docstrings for the input contract.
    # An "elevation scene glist" is a one-object glist whose base geometry
    # is a terrain heightmap (e.g. terrain_elevation.glist below).
    elevationGListPath = Path("/workspaces/dirsig-channel/data/local/dirsig-shared/LWIR_Urban_Alt/geometry/terrain_elevation.glist")
    
    baseGeometry = glist.GlistBaseGeometry(elevationGListPath)
    terrainBundleObject = glist.Object(baseGeometry)
    
    sceneHdfpath = terrain_scene(terrainBundleObject)
    
    height = elevation(sceneHdfpath, 0, 0)
    print(height)
