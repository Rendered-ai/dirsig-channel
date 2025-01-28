
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

def terrain_scene(terrain_bundle_object):

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
    """ Get scene peak and normal vector for ray cast origin: "scene_tool summary /tmp/elevation.scene.hdf"
    Inputs:
        - file pat the the compiled scene,
        - location x and y in scene ENU coordinates
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

    result = subprocess.run(
            ["scene_tool", "raycast", "--origin", str(location_x), str(location_y), originAlt, "--direction", "0", "0", "-1", scene_hdf_path],
            capture_output=True,
            text=True,
            env=os.environ,
        )
    data = json.loads(result.stdout)
    
    locationZ = data[0]['hitPosition'][2]
    
    surfaceNormal = data[0]['hitNormal']
    
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
    rotationAngle = np.arccos(np.dot(objNormal, surfaceNormal))
    rotation = Rotation.from_rotvec(rotationAxis * rotationAngle)
    eulerAngles = rotation.as_euler('xyz') #radians
    if units == "degrees":
         eulerAngles = [a*180/np.pi for a in eulerAngles]

    return eulerAngles

    
if __name__ == "__main__":

    #elevationGListPath = Path("/workspaces/dirsig-channel/data/local/dirsig-shared/Sierra_Nevada/bundles/terrain/elevation.glist")
    #elevationGListPath = Path("/workspaces/dirsig-channel/data/local/dirsig-shared/Desert_Highway_v2/geometry/Terrain_elevation.glist")
    elevationGListPath = Path("/workspaces/dirsig-channel/data/local/dirsig-shared/LWIR_Urban_Alt/geometry/terrain_elevation.glist")
    
    baseGeometry = glist.GlistBaseGeometry(elevationGListPath)
    terrainBundleObject = glist.Object(baseGeometry)
    
    sceneHdfpath = terrain_scene(terrainBundleObject)
    
    height = elevation(sceneHdfpath, 0, 0)
    print(height)
