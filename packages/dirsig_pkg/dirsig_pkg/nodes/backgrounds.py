
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
import anatools.lib.context as ctx
from anatools.lib.node import Node
from anatools.lib.package_utils import get_volume_path
import os
from pathlib import Path
import dirfm.glist as glist
from dirfm.scene import SCENE
from dirfm import materials
from dirfm import frames
from dirsig_pkg.lib.scene_utils import terrain_scene, elevation, align_directions
from dirsig_pkg.lib.cluster_generator_random import RandomClusterGenerator
from dirsig_pkg.lib.object import AnaDirsigObject, file_to_objgen
from itertools import count

logger = logging.getLogger(__name__)
Counter = count(0)


def scene(scene_objects, location=(0, 0, 0), meta={}, tags=[]):
    """Create a dictionary for a scene.
        Output:
        - scene objects
        - scene group timezone
        - scene metadata
    """

    # An estimate to find the correct time zone based on position
    timezone = round(float(location.get_pos()[1])/15)
    
    bundle = {
        "sceneObjects": scene_objects,
        "timezone": timezone,
        "metadata": meta,
        "tags": tags}
    return {"Scene" : bundle}


def scene_object(scene_name):
    """Create a full spectrum scene.
    """
    sceneObj = SCENE(scene_name).set_properties("vis,nir,swir,mwir,lwir")
    dummyMaterial = materials.Material("SceneDummy", ID="999999")
    dummyMaterial.add_surface_properties(materials.WardBrdfSurfaceProperty([1,1],[1,1]))
    dummyMaterial.set_temp_solver(materials.DataDrivenTempSolver(100))
    sceneObj.add_material(dummyMaterial)

    return sceneObj


def match_objects_to_terrain(ana_object, elevation_glist_path):
    """ Update the position of each object instance as follows
    1. Raise the z value of the translation by the elevation of the terrain
    2. Optionally, rotate the object to match the terrain normal
    """
    if glist.StaticInstance not in [type(i) for i in ana_object.root.get_instances()]:
        return

    # Compile the elevation scene
    baseGeometry = glist.GlistBaseGeometry(elevation_glist_path)
    terrainBundleObject = glist.Object(baseGeometry)
    elevationHdfpath = terrain_scene(terrainBundleObject)

    for objInstance in ana_object.root.get_instances():
        if type(objInstance)==glist.StaticInstance:
            trans = objInstance.get_translation()
            e, surfaceNormal = elevation(elevationHdfpath, trans[0], trans[1])
            trans[2]+=e
            objInstance.set_translation(trans)

            if ana_object.match_slope:
                #Rotate the object to lay flat on the terrain
                rot = objInstance.get_rotation()
                eulerAngles = align_directions(surfaceNormal, [0,0,1], units='degrees')
                objInstance.set_rotation([eulerAngles[0], eulerAngles[1], rot[2]])


class SierraNevada(Node):
    """ Region of the Sierra Nevada - 150 x 150 km in size, low res scene
    """
    
    def exec(self):
        logger.info("Executing {}".format(self.name))
        
        #Define the scene object
        sceneObj = scene_object("Sierra Nevada")

        ### Create the background anchor terrain
        anchorName = "terrain"
        scene_path = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Sierra_Nevada"))
        terrain_bundle_path = scene_path / "bundles" / "terrain"    
        terrainBundleObject = glist.Object(glist.GlistBaseGeometry(terrain_bundle_path / "sierra_terrain.glist"))
        terrainBundleObject.add_instance(glist.StaticInstance(anchorName))
        sceneGlist =  glist.GLIST().add_object(terrainBundleObject)
        
        sceneObj.add_geometry("Terrain Object", sceneGlist)

        location = frames.GeodeticFrame(38.340480, -120.016527, 1984.1)
        sceneObj.set_origin(location)

        metadata={
            'Scene description': 'Sierra Nevada; Low Resolution; 150km150km',
            'Last update': 'Aug 20, 2024',
        }

        inputObjects = self.inputs['Objects']
        if inputObjects[0] is None:
            return scene([sceneObj], location=location, meta=metadata)
        
        #Add objects to the scene as a glist
        names = list()
        objectMetadata = []        
        objectGenerators = file_to_objgen(inputObjects, AnaDirsigObject)
        objectsGList = glist.GLIST()
        
        for generator in objectGenerators:
            anaObject = generator.exec() # trigger the generator
            objectMetadata.append({
                "name": anaObject.name,
                "modifiers": anaObject.modifiers,
            })
            #Add the instance to the glist
            objectsGList.add_object(anaObject.root)

            #Collect object names for abundance truth collection
            names.append(anaObject.name)
            
            #Update anchor names for binary instances
            for objInstance in anaObject.root.get_instances():
                if type(objInstance) in [glist.StaticInstanceBinary, glist.StaticInstanceBinaryFile]:
                    objInstance.set_anchor(anchorName)
            
            #Update object's elevation for static instances
            elevationGListPath = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Sierra_Nevada/bundles/terrain/elevation.glist"))
            match_objects_to_terrain(anaObject, elevationGListPath)

            sceneObj.add_geometry("Objects", objectsGList)

        metadata['Object Modifiers'] = objectMetadata
        return scene([sceneObj], location=location, meta=metadata, tags=names)


class DesertHighwayScene(Node):
    """
    7.8km x 6.0 km
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        from dirsig_pkg.lib.materials_large_desert import mml

        geom_path = (
            Path(get_volume_path("dirsig_pkg", "dirsig-shared:Desert_Highway_v2")) / "geometry"
        )
        anchorName = "terrain"
        desert = (
            glist.GLIST()
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("Terrain.glist")
                        .add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "Terrain.obj"),
                                glist.StaticInstance(anchorName,scale=[1000, 1000, 1000]),
                            )
                        )
                        .add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "Roads.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[-3000,-3000,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("Grass.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "Grass_01.obj"),
                                glist.Wavefront(geom_path / "obj" / "Grass_02.obj"),
                                glist.Wavefront(geom_path / "obj" / "Grass_03.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "Grass.instances"
                                ),
                            )
                            .add_material_variant(
                                "Blade00",
                                mml["Dry-Grass-0000"],
                                mml["Dry-Grass-0001"],
                                mml["Dry-Grass-0002"],
                                mml["Dry-Grass-0003"],
                                mml["Dry-Grass-0004"],
                                mml["Dry-Grass-0005"],
                                mml["Dry-Grass-0006"],
                                mml["Dry-Grass-0007"],
                            )
                            .add_material_variant(
                                "Blade01",
                                mml["Dry-Grass-0000"],
                                mml["Dry-Grass-0001"],
                                mml["Dry-Grass-0002"],
                                mml["Dry-Grass-0003"],
                                mml["Dry-Grass-0004"],
                                mml["Dry-Grass-0005"],
                                mml["Dry-Grass-0006"],
                                mml["Dry-Grass-0007"],
                            )
                            .add_material_variant(
                                "Blade02",
                                mml["Dry-Grass-0000"],
                                mml["Dry-Grass-0001"],
                                mml["Dry-Grass-0002"],
                                mml["Dry-Grass-0003"],
                                mml["Dry-Grass-0004"],
                                mml["Dry-Grass-0005"],
                                mml["Dry-Grass-0006"],
                                mml["Dry-Grass-0007"],
                            )
                            .add_material_variant(
                                "Blade03",
                                mml["Dry-Grass-0000"],
                                mml["Dry-Grass-0001"],
                                mml["Dry-Grass-0002"],
                                mml["Dry-Grass-0003"],
                                mml["Dry-Grass-0004"],
                                mml["Dry-Grass-0005"],
                                mml["Dry-Grass-0006"],
                                mml["Dry-Grass-0007"],
                            )
                            .add_material_variant(
                                "Blade04",
                                mml["Dry-Grass-0000"],
                                mml["Dry-Grass-0001"],
                                mml["Dry-Grass-0002"],
                                mml["Dry-Grass-0003"],
                                mml["Dry-Grass-0004"],
                                mml["Dry-Grass-0005"],
                                mml["Dry-Grass-0006"],
                                mml["Dry-Grass-0007"],
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[-3000,-3000,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("Shrubs.glist").add_object(
                            glist.Object(
                                glist.GlistBaseGeometry(
                                    geom_path
                                    / "bundles"
                                    / "Restio_eleocharis"
                                    / "Restio_eleocharis.glist"
                                ),
                                #glist.GlistBaseGeometry(
                                #    geom_path
                                #    / "bundles"
                                #    / "Euclea_racemosa"
                                #    / "Euclea_racemosa.glist"
                                #),
                                glist.Wavefront(geom_path / "obj" / "Brush_01.obj"),
                                glist.Wavefront(geom_path / "obj" / "Brush_02.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "Shrubs.instances"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[-3000,-3000,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("BigRocks.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "BigRock_01.obj"),
                                glist.Wavefront(geom_path / "obj" / "BigRock_02.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "BigRocks.instances"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[-3000,-3000,0]),
                )
            )
        )

        location = frames.GeodeticFrame(39.593, -2.1015, 0)
        sceneObj = (
            SCENE("solar")
            .set_origin(location)
            .set_properties("vis,nir")
            .add_geometry("Terrain", desert)
        )

        for key in mml.keys():
            sceneObj.add_material(mml[key])

        metadata={
            'scene description': 'Desert Highway; High Resolution; 6kmx6km',
            'Release Date': 'Pre-release Feb 2024',
        }

        inputObjects = self.inputs['Objects']
        if inputObjects[0] is None:
            return scene([sceneObj], location=location, meta=metadata)
        
        #Add objects to the scene as a glist
        names = list()
        objectMetadata = []        
        objectGenerators = file_to_objgen(inputObjects, AnaDirsigObject)
        objectsGList = glist.GLIST()
        for generator in objectGenerators:
            anaObject = generator.exec() # trigger the generator
            objectMetadata.append({
                "name": anaObject.name,
                "modifiers": anaObject.modifiers,
            })
            objectsGList.add_object(anaObject.root)

            #Collect object names for abundance truth collection
            names.append(anaObject.name)
            
            #Update anchor names for binary instances
            for objInstance in anaObject.root.get_instances():
                if type(objInstance) in [glist.StaticInstanceBinary, glist.StaticInstanceBinaryFile]:
                    objInstance.set_anchor(anchorName)
            
            #Update object's elevation for static instances
            elevationGListPath = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Desert_Highway_v2/geometry/Terrain_elevation.glist"))
            match_objects_to_terrain(anaObject, elevationGListPath)

        sceneObj.add_geometry("Objects", objectsGList)

        metadata['Object Modifiers'] = objectMetadata
        
        return scene([sceneObj], location=location, meta=metadata, tags=names)
    

class LWIRUrbanAltScene(Node):
    """
    3m x 3km
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        from dirsig_pkg.lib.materials_lwir_urban_alt import mml

        geom_path = (
            Path(get_volume_path("dirsig_pkg", "dirsig-shared:LWIR_Urban_Alt")) / "geometry"
        )
        anchorName = "terrain"
        urban = (
            glist.GLIST()
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("terrain.glist")
                        .add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "terrain.obj"),
                                glist.StaticInstance("terrain"),
                            )
                        )
                        .add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "roads.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_tall_1.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_tall_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_tall_1_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_tall_1_roof_junk.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_tall_1_roof_junk_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_tall_1_roof_junk_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_tall_2.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_tall_2.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_tall_2_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_tall_2_roof_junk.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_tall_2_roof_junk_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_tall_2_roof_junk_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_tall_3.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_tall_3.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_tall_3_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_1.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_1_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_1_roof_junk.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_1_roof_junk_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_1_roof_junk_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_2.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_2.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_2_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_2_roof_junk.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_2_roof_junk_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_2_roof_junk_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_3.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_3.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_3_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_3_roof_junk.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_3_roof_junk_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_3_roof_junk_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_commercial_part_wide_4.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_commercial_part_wide_4.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_commercial_part_wide_4_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_residential_1.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_residential_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_residential_1_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("building_residential_2.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "building_residential_2.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "building_residential_2_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("detritus.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "detritus_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "detritus_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("dumpster.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "dumpster.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "dumpster_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("grass.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "grass_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "grass_2.obj"),
                                glist.Wavefront(geom_path / "obj" / "grass_3.obj"),
                                glist.Wavefront(geom_path / "obj" / "grass_4.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "grass_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object( # this model had a facet issue, likely due to an ngon
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("mailbox_residential.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "mailbox_residential.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("mailbox_usps.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "mailbox_usps.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "mailbox_usps_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("power_line.glist").add_object(
                            glist.Object(
                                glist.GlistBaseGeometry(
                                    geom_path / "generated" / "power_line.glist"
                                ),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("power_pole.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "power_pole_12m.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "power_pole_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("rock.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "rock_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "rock_2.obj"),
                                glist.Wavefront(geom_path / "obj" / "rock_3.obj"),
                                glist.Wavefront(geom_path / "obj" / "rock_4.obj"),
                                glist.Wavefront(geom_path / "obj" / "rock_5.obj"),
                                glist.Wavefront(geom_path / "obj" / "rock_6.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0],anchor='terrain'),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("shrub.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "shrub_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "shrub_2.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0],anchor='terrain'),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("street_light_short.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "street_light_short.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "street_light_short_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("street_light_tall_traffic_light.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "street_light_tall_traffic_light.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "street_light_tall_traffic_light_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("street_light_tall.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "street_light_tall.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "street_light_tall_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("street_sign.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "street_sign_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "street_sign_2.obj"),
                                glist.Wavefront(geom_path / "obj" / "street_sign_3.obj"),
                                glist.Wavefront(geom_path / "obj" / "street_sign_4.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "street_sign_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("subcanopy.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "subcanopy_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "subcanopy_2.obj"),
                                glist.Wavefront(geom_path / "obj" / "subcanopy_3.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "subcanopy_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("traffic_cone.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "traffic_cone.obj"),
                                glist.StaticInstance(),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("trash_can.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "trash_can.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "trash_can_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("tree_conif_large.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "tree_conif_large_1.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "tree_conif_large_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("tree_decid_large.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "tree_decid_large_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "tree_decid_large_2.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "tree_decid_large_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
            .add_object(
                glist.Object(
                    glist.GlistBaseGeometry(
                        glist.GLIST("tree_decid_small.glist").add_object(
                            glist.Object(
                                glist.Wavefront(geom_path / "obj" / "tree_decid_small_1.obj"),
                                glist.Wavefront(geom_path / "obj" / "tree_decid_small_2.obj"),
                                glist.Wavefront(geom_path / "obj" / "tree_decid_small_3.obj"),
                                glist.StaticInstanceBinaryFile(
                                    geom_path / "generated" / "tree_decid_small_positions.bin"
                                ),
                            )
                        )
                    ),
                    glist.StaticInstance(translation=[0,0,0]),
                )
            )
        )

        location = frames.GeodeticFrame(3.15, -77.61, 0)
        sceneObj = (
            SCENE("solar")
            .set_origin( location)
            .set_properties("vis,nir")
            .add_geometry("terrain", urban)
        )

        for key in mml.keys():
            sceneObj.add_material(mml[key])

        metadata={
            'scene description': 'LWIR Urban Procedural; High Resolution; 3kmx3km',
            'Release Date': 'Pre-release Feb 2024',
        }

        inputObjects = self.inputs['Objects']
        if inputObjects[0] is None:
            return scene([sceneObj], location=location, meta=metadata)
        
        #Add objects to the scene as a glist
        names = list()
        objectMetadata = []        
        objectGenerators = file_to_objgen(inputObjects, AnaDirsigObject)
        objectsGList = glist.GLIST()
        for generator in objectGenerators:
            anaObject = generator.exec() # trigger the generator
            objectMetadata.append({
                "name": anaObject.name,
                "modifiers": anaObject.modifiers,
            })
            objectsGList.add_object(anaObject.root)

            #Collect object names for abundance truth collection
            names.append(anaObject.name)
            
            #Update anchor names for binary instances
            for objInstance in anaObject.root.get_instances():
                if type(objInstance) in [glist.StaticInstanceBinary, glist.StaticInstanceBinaryFile]:
                    objInstance.set_anchor(anchorName)
            
            #Update object's elevation for static instances
            elevationGListPath = Path(get_volume_path("dirsig_pkg", "dirsig-shared:LWIR_Urban_Alt/geometry/terrain_elevation.glist"))
            match_objects_to_terrain(anaObject, elevationGListPath)
            
        sceneObj.add_geometry("Objects", objectsGList)

        metadata['Object Modifiers'] = objectMetadata
        return scene([sceneObj], location=location, meta=metadata,tags=names)
