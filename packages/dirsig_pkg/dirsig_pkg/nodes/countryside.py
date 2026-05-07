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
import glob
import os
import csv
import numpy as np
import math
from shapely.geometry import Polygon
from multiprocessing import Pool
from lxml import etree as et
import anatools.lib.context as ctx
from anatools.lib.node import Node
from anatools.lib.package_utils import get_volume_path
import dirfm.glist as glist
from dirfm.scene import SCENE, DecalMap
from dirfm import materials
import dirfm.glist as glist
from dirfm import frames
from dirfm.utilities.grid_position_generator import grid_position_generator
from dirsig_pkg.lib.scene_utils import terrain_scene, elevation, align_directions
from dirsig_pkg.lib.object import AnaDirsigObject, file_to_objgen
from dirsig_pkg.lib.materials_large_desert import mml, map_path

logger = logging.getLogger(__name__)

# Define the location of the scene assets
scene_path = (
    Path(get_volume_path("dirsig_pkg", "dirsig-shared:Europe7km-11-July-2024")) / "Europe7km"
)


def make_locations(parcel_idx, di, sp, ro, dev, poly):
    """Generate locations for a parcel using grid position generator."""
    
    #mask (Polygon, optional): A Polygon object to mask out grid positions outside of its boundary.
    locations = grid_position_generator(di, sp, ro, dev, poly)
    locationsFilepath = Path("/tmp") / f"parcel{parcel_idx}.bin"
    sib = glist.StaticInstanceBinary(fname=str(locationsFilepath))
    for loc in locations:
        sib.add_instance(translation=loc, rotation=[0, 0, ctx.random.random() * 360])
    root = et.Element("geometrylist", enabled="true")
    sib.write(root, {"geometry": Path.cwd()})
    return locationsFilepath


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
    sceneObj = SCENE(scene_name).set_properties("vis,nir,swir")
    
    # Set up directories like the working implementation
    dirs = {
        'root': Path("/tmp"),
        'maps': Path("/tmp/maps"),
        'material': Path("/tmp/materials"),
        'geometry': Path("/tmp/geometry"),
    }
    
    for d in dirs.values():
        if not os.path.isdir(str(d)):
            os.makedirs(str(d), exist_ok=True)
            
    sceneObj.set_ems_dir(dirs["material"])
    sceneObj.set_ext_dir(dirs["material"])
    sceneObj.set_abs_dir(dirs["material"])
    sceneObj.set_src_dir(dirs["material"])
    sceneObj.set_map_dir(dirs["maps"])
    
    return sceneObj


def region_bundle_object(region, region_type, anchor_name, verticies):
    """A glist Object for a region of the scene based on a DIRSIG bundle of a region type."""
    # Get the bundle object from the biome data (region_type)
    if isinstance(region_type, dict):
        # region_type is already the biome data dict from the linked node output
        bundleObject = region_type['bundle_object']
        di = region_type.get('dims', [400, 400])
        sp = region_type.get('spacing', [1.5, 1.5])
        dev = region_type.get('deviation', 0.75)
    else:
        # Fallback to desert if no biome node is linked (region_type could be "Desert" string)
        bundleObject = glist.Object(
            glist.GlistBaseGeometry(scene_path / "bundles" / "Euclea_racemosa" / "Euclea_racemosa.glist"),
        )
        di = [70, 70]
        sp = [10, 10]
        dev = 5
    
    # Generate parcel locations using multiprocessing
    rot = ctx.random.randint(0,360)
    
    # Create jobs for multiprocessing
    jobs = []
    for parcelIdx in region['parcels']:
        jobs.append((parcelIdx, di, sp, rot, dev, Polygon(verticies[parcelIdx])))
    
    with Pool() as pool:
        locFilepaths = pool.starmap(make_locations, jobs)
    
    # Add instances to the bundle object
    for locationsFilepath in locFilepaths:
        bundleObject.add_instance(glist.StaticInstanceBinaryFile(locationsFilepath, anchor=anchor_name))
    
    return bundleObject

def create_terrain(sceneObj):
    """Creates and adds the terrain geometry and materials to the scene object."""
    # Create three soil materials with different reflectance data
    for soil_idx in range(3):
        name = "Soil-{:04d}".format(soil_idx)
        soil_r = np.loadtxt(scene_path / "materials" / "curves" / "Soil-{:04d}.txt".format(soil_idx))
        soil_material = (
            materials.Material(name, True, ID=name)
            .set_rad_solver(materials.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                materials.ThermTempSolver(
                    specific_heat=0.370,
                    mass_density=1.7,
                    thermal_conductivity=2.158,
                    solar_absorption=0.73,
                    thermal_emissivity=0.9,
                    exposed_area=0.5,
                    thickness=5,
                )
            )
            .add_surface_properties(
                materials.SimpleReflectanceSurfaceProperty(soil_r[:, 0], soil_r[:, 1])
            )
        )
        mml.add_entry(soil_material)
        sceneObj.add_material(soil_material)

    # Create the terrain material with material map
    terrain_material = (
        materials.Material("Terrain", True, ID="terrain")
        .set_rad_solver(materials.SimpleRadiationSolver("LOW"))
        .set_normal_map(
            materials.NormalMap(
                map_path / "Dirt-Normal.jpg",
                materials.DrapeProjection(
                    [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                ),
            )
        )
        .set_material_map(
            materials.MaterialMap(
                "Gradient",
                scene_path / "bundles" / "terrain" / "maps" / "Terrain.png",
                materials.DrapeProjection([0, 0], 6, origin="cartesian"),
                [(0, mml["Soil-0000"]), (128, mml["Soil-0001"]), (255, mml["Soil-0002"])],
            )
        )
    )
    
    mml.add_entry(terrain_material)
    sceneObj.add_material(terrain_material) 
    
    # Add terrain geometry and assign the material
    terrainGLIST = (
        glist.GLIST("Terrain.glist").add_object(
            glist.Object(
                glist.Wavefront(scene_path / "geometry" / "terrain.obj"),
                glist.StaticInstance(),
            )
        )
    )
    terrainObject = glist.Object(glist.GlistBaseGeometry(terrainGLIST))
    terrainObject.add_instance(glist.StaticInstance("terrain"))
    sceneObj.add_geometry("Terrain", glist.GLIST().add_object(terrainObject))

def align_objects_with_terrain(ana_object, elevationHdfpath, anchor_name=None, location=[0,0,0]):
    """ Update the position of each object instance as follows
    1. Raise the z value of the translation by the elevation of the terrain
    2. Optionally, rotate the object to match the terrain normal
    """
    #Set anchors for all instances of objects
    if ana_object.match_elevation:
        for objInstance in ana_object.root.get_instances():
            if type(objInstance) is not glist.DynamicInstance:
                objInstance.set_anchor(anchor_name)

    # Only objects with static instances can be explicitly aligned with terrain
    if glist.StaticInstance not in [type(i) for i in ana_object.root.get_instances()]:
        return

    # Update the position of each object instance
    for objInstance in ana_object.root.get_instances():
        if type(objInstance) == glist.StaticInstance:
            trans = objInstance.get_translation()
            e, surfaceNormal = elevation(elevationHdfpath, int(trans[0]), int(trans[1]))
            
            trans[2]+=e
            objInstance.set_translation(trans)

            if ana_object.name == "Trees":
                # The trees glist is a population and cannot be anchored.
                # It must be included directly.
                sceneObj.add_geometry_include(ana_object.root.get_base_geometry()[0]._glist)
            else:
                if ana_object.match_slope:
                    #Rotate the object to lay flat on the terrain
                    rot = objInstance.get_rotation()
                    eulerAngles = align_directions(surfaceNormal, [0,0,1], units='degrees')
                    objInstance.set_rotation([eulerAngles[0], eulerAngles[1], rot[2]])


class Countryside(Node):
    """ A minimal scene with terrain and trees
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        # Define the scene object
        sceneObj = scene_object("Contryside_Scene")
        
        # Set scene location and origin
        location = frames.GeodeticFrame(44.685, 10.2172, 0.000)
        sceneObj.set_origin(location)
        
        # Create the background terrain
        anchorName = "terrain"
        create_terrain(sceneObj)
        
        # Add roads as decal maps
        roadGlistPath = scene_path / "bundles" / "roads" / "decalMaps.glist"
        roadDecal = DecalMap('Road Decal Map', 'terrain', roadGlistPath)
        sceneObj.add_decal_map(roadDecal)
        
        # Add trees if enabled
        use_trees_input = self.inputs.get("Use Trees")[0]
        if use_trees_input == 'True':
            treesBundleObject = glist.Object(glist.GlistBaseGeometry(scene_path / "bundles" / "trees" / "trees.glist"))
            treeLocationsFilepath = scene_path / "treeInstances.bin"
            treesBundleObject.add_instance(glist.StaticInstanceBinaryFile(treeLocationsFilepath, anchor=anchorName))
            sceneObj.add_geometry("Trees", glist.GLIST().add_object(treesBundleObject))
            logger.info("Added trees to the scene")
        else:
            logger.info(f"User disabled trees")
        

        # Add parcels/regions
        regions = {
            "central":  {'parcels': [102, 115, 121, 109, 119, 117, 128, 123, 122, 124]},
            "northern": {'parcels': [83, 88, 85, 91, 93, 99, 86, 90, 87, 92, 96, 118, 114, 116, 95,94, 89, 112, 110, 120, 113, 111, 97, 107, 104, 101, 547, 108]},
            "eastern":  {'parcels': [552, 555, 554, 551, 59, 100, 550, 60, 586, 585, 549, 584, 589, 548]},
            "southern": {'parcels': [544, 545, 542, 539, 540, 538, 295, 561, 562, 567, 565, 558, 560, 279, 559]},
            "western":  {'parcels': [138, 130, 156, 157, 155, 534, 535, 125, 126, 127, 543, 541]},
            #"western":  {'parcels': [138, 130, 156, 157, 155, 534, 535, 125, 126, 127, 543, 541, 597, 536, 58]},
        }
        
        # Load parcel vertices
        verticies = {}
        for verticiesFilepath in glob.glob(str(scene_path / "parcelBorderVerticesInOrder" / "*")):
            parcelIdx = int(os.path.basename(verticiesFilepath).split("_")[0].strip("parcel"))
            with open(verticiesFilepath, 'r') as f:
                parcelVerticies = list(csv.reader(f))
            verticies[parcelIdx] = [[float(value) for value in row[0].split()] for row in parcelVerticies]


        # Add regions based on inputs
        regionsGList = glist.GLIST()
        for regionName in ["Central", "Northern", "Eastern", "Southern", "Western"]:
            linked_biomes = self.inputs.get(f"{regionName} Region")
            if linked_biomes[0] in [None, '']:
                # Default to "Desert" if no biome nodes are linked
                regionInput = "Desert"
                logger.info(f"{regionName} Region: Using default Desert biome")
            else:
                # Randomly choose one of the linked biomes
                regionInput = ctx.random.choice(linked_biomes)
                logger.info(f"{regionName} Region: Selected '{regionInput.get('Biome', 'Unknown')}' from {len(linked_biomes)} linked biomes (seed: {ctx.seed}, interp_num: {ctx.interp_num})")
            regionBundleObject = region_bundle_object(regions[regionName.lower()], regionInput, anchorName, verticies)
            regionsGList.add_object(regionBundleObject)
        
        sceneObj.add_geometry("Regions", regionsGList)
        
        # Add towers and cables
        cableThickness = 0.05
        
        # Create a cable material based on cable type
        cableMaterialId = "cable"
        cableType = self.inputs.get('Cable Type', ['Aluminum'])[0]
        cableMaterial = materials.Material("Power line", double_sided=True, ID=cableMaterialId)
        
        if cableType == "Copper":
            # Copper cable properties - more reflective with reddish tint
            cableMaterial.add_surface_properties(
                materials.WardBrdfSurfaceProperty(
                    ds_weights=[0.7, 0.5],  # Copper reflectance
                    xy_sigmas=[0.1, 0.1],
                )
            )
        else:  # Default to Aluminum
            # Aluminum cable properties - using brushed aluminum BRDF
            cableParameterFile = scene_path / "materials" / "brushedAluminium" / "al-crc-0125.TS.brdf"
            enableDiffuseContribution=True
            enableShadowingFunction=True
            cableMaterial.add_surface_properties(
                materials.PriestGermerBrdfSurfaceProperty(
                    parameter_file=cableParameterFile,
                    enable_diffuse_contribution=enableDiffuseContribution,
                    enable_shadowing_function=enableShadowingFunction,
                )
            )
        sceneObj.add_material(cableMaterial)

        # Define the towers and cables
        towerInput = self.inputs.get('Tower Type', ['Tower 1'])[0]
        if towerInput == "<random>":
            towerInput = ctx.random.choice([f"Tower {i+1}" for i in range(5)])
        towerType = towerInput.split(" ")[1]
        
        bundle1Filepath = scene_path / "bundles" / "tower" / f"tower{towerType}.glist"
        offset1Filepath = scene_path / "bundles" / "tower" / "geometry"/ f"tower{towerType}_locatorPositions.csv"
        
        tower_cable_names = []  # Initialize outside try block
        # Track span->cable mapping for annotation metadata
        span_to_cable = {}
        try:
            with open(offset1Filepath, newline="") as f:
                offsets = list(csv.reader(f))

            # Group 1 is along the road near the NW boarder
            # Groups 1,2,3,4 get close to the SW boarder and trace SW-NE
            # Group 5 marks an E/W path through the center
            # Groups 6,7,8,1 get close to the NE boarder and trace SW-NE
            towersGList = glist.GLIST(tags=['tower'])
            cablesGList = glist.GLIST(tags=['cable'])
            for groupNumber in range(6):
                positionsFilepath = scene_path / "towerdata" / f"positions_towerGroup{groupNumber+1}.csv"

                try:
                    with open(positionsFilepath, newline="") as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                    def positionDict(row):
                        return {
                            'Tower Name': row[0],
                            'Scene Location': [float(r) for r in row[1:4]],
                            'Rotation': [float(r) for r in row[4:7]],
                            'Sag': float(row[7]),
                        }
                    positions = [positionDict(r) for i,r in enumerate(rows) if i>0]
                    
                    # Define glists for towers and cables
                    for towerPositionIdx in range(len(positions)-1):
                        logger.info(f"Adding {positions[towerPositionIdx]['Tower Name']} (group {groupNumber+1})")
                        tower = glist.Object(glist.GlistBaseGeometry(bundle1Filepath))
                        translation = positions[towerPositionIdx]['Scene Location']
                        rotation = positions[towerPositionIdx]['Rotation']
                        # Ensure each tower has a unique name by suffixing with its group number
                        tower_name = f"{positions[towerPositionIdx]['Tower Name']}-G{groupNumber+1}"
                        tower.add_instance(glist.StaticInstance(name=tower_name, translation=translation, rotation=rotation))
                        towersGList.add_object(tower)
                        tower_cable_names.append(tower_name)
                        
                        thisAttach = [None] * len(offsets)
                        for ii, offset in enumerate(offsets):
                            
                            xNaught=float(offset[1])
                            yNaught=float(offset[2])
                            alphaNaught = math.atan(yNaught/xNaught)
                            alpha = float(rotation[2])*math.pi/180 + alphaNaught
                            # r = math.sqrt(xNaught**2 + yNaught**2)
                            xOffset = xNaught*math.cos(alpha)
                            yOffset = xNaught*math.sin(alpha)
                            thisAttach[ii] = [t+o for t,o in zip(translation, [xOffset,yOffset,float(offset[3])])]
                            
                            if towerPositionIdx>0:
                                cableSag = positions[towerPositionIdx]['Sag']
                                cable = glist.Object(
                                    glist.CatenaryCurve(initAttach[ii], thisAttach[ii], cableThickness, cableSag, cableMaterialId)
                                )
                                # Tag cables per span with a standardized, tower-agnostic identifier per group+segment index
                                # Use zero-padded index for stable sorting in downstream tools
                                span_name = f"CableSpan-G{groupNumber+1}-{towerPositionIdx:03d}"
                                cable_instance_name = f"Cable {span_name}"
                                cable.add_instance(glist.StaticInstance(name=cable_instance_name))
                                cablesGList.add_object(cable)
                                tower_cable_names.append(cable_instance_name)
                                # Map span to its parent cable run (group-based) for metadata
                                cable_id = f"CableRun-G{groupNumber+1}"
                                span_to_cable[span_name] = cable_id

                        initAttach = thisAttach
                except FileNotFoundError as e:
                    logger.warning(f"Could not find tower positions file: {positionsFilepath}")
                    continue
                        
            sceneObj.add_geometry("Towers", towersGList)
            sceneObj.add_geometry("Cables", cablesGList)
            logger.info("Added towers and cables to the scene")
        except FileNotFoundError as e:
            logger.warning(f"Could not add towers and cables to the scene: {e}")
        
        # Tower and cable names are already collected during creation above
        
        # Process user-provided objects
        metadata = {
            'scene description': 'Europe Cable Scene; 7kmx7km',
            'Release Date': 'September 2025',
        }
        # Include span-to-cable mapping in scene metadata for downstream annotation
        if span_to_cable:
            metadata['span_to_cable'] = span_to_cable
        
        inputObjects = self.inputs.get('Objects', None)
        
        # Check if infrastructure should be included in annotations
        include_infrastructure = self.inputs.get('Include Infrastructure in Annotations', ['True'])[0]
        if include_infrastructure == 'True':
            names = tower_cable_names.copy()  # Start with tower and cable names
        else:
            names = []  # Start with empty list, excluding infrastructure from annotations
        
        if inputObjects is not None:
            # Add objects to the scene as a glist
            objectMetadata = []        
            objectGenerators = file_to_objgen(inputObjects, AnaDirsigObject)
            objectsGList = glist.GLIST()
            
            # Compile elevation scene once before processing objects
            elevationGListPath = scene_path / "bundles" / "terrain" / "terrain-dirt.glist"
            elevationHdfpath = self._compile_elevation_scene(elevationGListPath)

            for generator in objectGenerators:
                if not generator:
                    continue
                anaObject = generator.exec()  # trigger the generator
                if not anaObject:
                    continue
                objectMetadata.append({
                    "name": anaObject.name,
                    "modifiers": anaObject.modifiers,
                })
                # Add the instance to the glist
                objectsGList.add_object(anaObject.root)
                
                # Update object's elevation for static instances
                align_objects_with_terrain(anaObject, elevationHdfpath, anchorName)
                
                # Collect object instance names for abundance truth collection
                for objInstance in anaObject.root.get_instances():
                    names.append(objInstance.get_name())
            
            sceneObj.add_geometry("Objects", objectsGList)
            metadata['Object Modifiers'] = objectMetadata
        
        # Deduplicate tag names before returning the scene so the truth collection receives unique tags
        unique_names = sorted(set(names))
        return scene([sceneObj], location=location, meta=metadata, tags=unique_names)

    def _compile_elevation_scene(self, elevation_glist_path):
        """Compile the elevation scene and return the HDF file path."""
        baseGeometry = glist.GlistBaseGeometry(elevation_glist_path)
        terrainBundleObject = glist.Object(baseGeometry)
        return terrain_scene(terrainBundleObject)


class GrassBiome(Node):
    """Represents the Grass biome."""

    def exec(self):
        logger.info(f"Executing {self.name}")
        bundleObject = glist.Object(glist.GlistBaseGeometry(scene_path / "bundles" / "grass" / "grass.glist"))
        
        # Get density preference
        density = self.inputs.get('Density', ['Lush & Thick'])[0]
        
        # Handle random selection
        if density == '<random>':
            import random
            density = random.choice(['Lush & Thick', 'Thin & Clumpy'])
        
        if density == 'Thin & Clumpy':
            # More spacing, more deviation for clumpy appearance
            spacing = [5.0, 5.0]
            deviation = 5.0
        else:  # Lush & Thick
            # Less spacing, less deviation for dense appearance
            spacing = [1.5, 1.5]
            deviation = 0.75
        
        return {
            "Biome": {
                "Biome": "Grass",
                "bundle_object": bundleObject,
                "dims": [400, 400],
                "spacing": spacing,
                "deviation": deviation
            }
        }


class WheatBiome(Node):
    """Represents the Wheat biome."""

    def exec(self):
        logger.info(f"Executing {self.name}")
        bundleObject = glist.Object(glist.GlistBaseGeometry(scene_path / "bundles" / "wheat" / "wheat.glist"))
        return {
            "Biome": {
                "Biome": "Wheat",
                "bundle_object": bundleObject,
                "dims": [1000, 1000],
                "spacing": [0.5, 0.5],
                "deviation": 0.3
            }
        }


class CornBiome(Node):
    """Represents the Corn biome."""

    def exec(self):
        logger.info(f"Executing {self.name}")
        bundleObject = glist.Object(glist.GlistBaseGeometry(scene_path / "bundles" / "corn" / "corn.glist"))
        return {
            "Biome": {
                "Biome": "Corn",
                "bundle_object": bundleObject,
                "dims": [1500, 400],
                "spacing": [0.30, 0.75],  # spacing between planted rows, spacing between rows
                "deviation": 0.1
            }
        }


class DesertBiome(Node):
    """Represents the Desert biome."""

    def exec(self):
        logger.info(f"Executing {self.name}")
        bundleObject = glist.Object(
            glist.GlistBaseGeometry(scene_path / "bundles" / "Euclea_racemosa" / "Euclea_racemosa.glist"),
            glist.GlistBaseGeometry(scene_path / "bundles" / "Restio_eleocharis" / "Restio_eleocharis.glist"),
        )
        return {
            "Biome": {
                "Biome": "Desert",
                "bundle_object": bundleObject,
                "dims": [70, 70],
                "spacing": [10, 10],
                "deviation": 5
            }
        }
