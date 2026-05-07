
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

from pathlib import Path
import numpy as np

from dirfm import materials as m
from dirfm.utilities.material_manager import MasterMaterialList

from anatools.lib.package_utils import get_volume_path

map_path = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Desert_Highway_v2")) / "maps"
curve_path = (
    Path(get_volume_path("dirsig_pkg", "dirsig-shared:Desert_Highway_v2")) / "materials" / "curves"
)
forest_materials_path = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Forest")) / "materials"
europe_materials_path = Path(get_volume_path("dirsig_pkg", "dirsig-shared:Europe7km-11-July-2024")) / "Europe7km" / "materials"

def create_mml(road_type="Paved"):
    """Create and return a MasterMaterialList with configurable road type.
    
    Args:
        road_type: "Paved" or "Dirt"
    
    Returns:
        MasterMaterialList with all materials
    """
    mml = MasterMaterialList()

    
    dry_grass_t = np.loadtxt(curve_path / "Dry-Grass-0000.T.txt")
    dry_grass_r = np.loadtxt(curve_path / "Dry-Grass-0000.R.txt")
    asphalt_r = np.loadtxt(curve_path / "asphalt_01.txt")
    # No dedicated rock curve ships in this volume; concrete_01 is the closest mineral/grey
    # match (~30% albedo). Avoid asphalt_r for Rock — it makes rocks look ~5% black.
    rock_r = np.loadtxt(curve_path / "concrete_01.txt")

    mml.add_entry(
        m.Material("Brush", True, ID="brush")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.3703,
                mass_density=1.7,
                thermal_conductivity=2.15,
                solar_absorption=0.73,
                thermal_emissivity=0.9,
                exposed_area=0.5,
                thickness=5,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(dry_grass_r[:, 0], dry_grass_r[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(dry_grass_t[:, 0], dry_grass_t[:, 1])
        )
    )

    mml.add_entry(
        m.Material("Rock", True, ID="Rock")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.5087,
                mass_density=0.9,
                solar_absorption=0.95,
                thermal_conductivity=18.508,
                thermal_emissivity=0.658,
                exposed_area=0.4103,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(rock_r[:, 0], rock_r[:, 1])
        )
    )

    # Road body: asphalt for Paved, dirt for Dirt.
    if road_type == "Paved":
        mml.add_entry(
            m.Material("Road", True, ID="Road")
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
                    specific_heat=0.5087,
                    mass_density=0.9,
                    solar_absorption=0.95,
                    thermal_conductivity=18.508,
                    thermal_emissivity=0.658,
                    exposed_area=0.4103,
                    thickness=1,
                )
            )
            .add_surface_properties(
                m.SimpleReflectanceSurfaceProperty(asphalt_r[:, 0], asphalt_r[:, 1])
            )
            .set_normal_map(
                m.NormalMap(
                    map_path / "Asphalt-Normal.png",
                    m.DrapeProjection(
                        [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                    ),
                )
            )
        )
    else:
        mml.add_entry(
            m.Material("Road", True, ID="Road")
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
                    specific_heat=0.5087,
                    mass_density=0.9,
                    solar_absorption=0.95,
                    thermal_conductivity=18.508,
                    thermal_emissivity=0.658,
                    exposed_area=0.4103,
                    thickness=1,
                )
            )
            .add_surface_properties(
                m.ClassicEmissivitySurfaceProperty(
                    ems=europe_materials_path / "dirt_micro_no.ems",
                    specularity=0
                )
            )
            .set_normal_map(
                m.NormalMap(
                    map_path / "Dirt-Normal.jpg",
                    m.DrapeProjection(
                        [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                    ),
                )
            )
        )

    # WhiteLine: bright matte white paint on Paved roads; blends into dirt when unpaved.
    if road_type == "Paved":
        mml.add_entry(
            m.Material("WhiteLine", True, ID="WhiteLine")
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
                    specific_heat=0.5087,
                    mass_density=0.9,
                    solar_absorption=0.95,
                    thermal_conductivity=18.508,
                    thermal_emissivity=0.658,
                    exposed_area=0.4103,
                    thickness=1,
                )
            )
            # Ward BRDF: ~70% diffuse + low specular + slight roughness ~ matte white paint.
            .add_surface_properties(m.WardBrdfSurfaceProperty([0.7, 0.05], [0.1, 0.1]))
            .set_normal_map(
                m.NormalMap(
                    map_path / "Asphalt-Normal.png",
                    m.DrapeProjection(
                        [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                    ),
                )
            )
        )
    else:
        # For dirt roads, make WhiteLine look like dirt (same as Road)
        mml.add_entry(
            m.Material("WhiteLine", True, ID="WhiteLine")
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
                    specific_heat=0.5087,
                    mass_density=0.9,
                    solar_absorption=0.95,
                    thermal_conductivity=18.508,
                    thermal_emissivity=0.658,
                    exposed_area=0.4103,
                    thickness=1,
                )
            )
            .add_surface_properties(
                m.ClassicEmissivitySurfaceProperty(
                    ems=europe_materials_path / "dirt_micro_no.ems",
                    specularity=0
                )
            )
            .set_normal_map(
                m.NormalMap(
                    map_path / "Dirt-Normal.jpg",
                    m.DrapeProjection(
                        [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                    ),
                )
            )
        )

    soil_idx_list = [0, 2, 5]
    for soil_idx in range(3):
        name = "Soil-{:04d}".format(soil_idx)
        soil_r = np.loadtxt(curve_path / "Soil-{:04d}.txt".format(soil_idx))
        mml.add_entry(
            m.Material(name, True, ID=name)
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
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
                m.SimpleReflectanceSurfaceProperty(soil_r[:, 0], soil_r[:, 1])
            )
        )

    mml.add_entry(
        m.Material("Terrain", True, ID="Terrain")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_normal_map(
            m.NormalMap(
                map_path / "Asphalt-Normal.png",
                m.DrapeProjection(
                    [0, 0], 0.001, origin="cartesian", extendx="repeat", extendy="repeat"
                ),
            )
        )
        .set_material_map(
            m.MaterialMap(
                "Gradient",
                map_path / "Terrain.png",
                m.DrapeProjection([0, 0], 6, origin="cartesian"),
                [(0, mml["Soil-0000"]), (128, mml["Soil-0001"]), (255, mml["Soil-0002"])],
            )
        )
    )

    for grass_idx in range(8):
        name = "Dry-Grass-{:04d}".format(grass_idx)
        grass_r = np.loadtxt(curve_path / "Dry-Grass-{:04d}.R.txt".format(grass_idx))
        grass_t = np.loadtxt(curve_path / "Dry-Grass-{:04d}.T.txt".format(grass_idx))
        mml.add_entry(
            m.Material(name, True, ID=name)
            .set_rad_solver(m.SimpleRadiationSolver("LOW"))
            .set_temp_solver(
                m.ThermTempSolver(
                    specific_heat=0.376,
                    mass_density=1.09,
                    thermal_conductivity=2.18,
                    thermal_emissivity=0.988,
                    exposed_area=-0.69448,
                    thickness=0.0525,
                )
            )
            .add_surface_properties(
                m.SimpleReflectanceSurfaceProperty(grass_r[:, 0], grass_r[:, 1])
            )
            .add_surface_properties(
                m.SimpleTransmittanceSurfaceProperty(grass_t[:, 0], grass_t[:, 1])
            )
        )
    
    return mml

# Create default mml for backward compatibility
mml = create_mml()

