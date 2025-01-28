
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

mml = MasterMaterialList()

map_path = Path(get_volume_path("dirsig_pkg", "dirsig-shared:LWIR_Urban_Alt")) / "maps"
curve_path = (
    Path(get_volume_path("dirsig_pkg", "dirsig-shared:LWIR_Urban_Alt")) / "materials" / "curves"
)

terrain_r = np.loadtxt(curve_path / "soil.txt")

mml.add_entry(
    m.Material("Terrain", True, ID="Terrain")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_bump_map(
        m.BumpMap(
            "dirt_bump",
            map_path / "dirt_bump.jpg",
            m.DrapeProjection(
                [0, 0], 0.01, origin="cartesian", extendx="repeat", extendy="repeat"
            ),
            0.1,
        )
    )
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
        m.SimpleReflectanceSurfaceProperty(terrain_r[:, 0], terrain_r[:, 1])
    )
)

mml.add_entry(
    m.Material("Tree", True, ID="Tree")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.12, 0]))
)

mml.add_entry(
    m.Material("Plastic", True, ID="Plastic")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=1.3,
            mass_density=4.0,
            solar_absorption=0.7,
            thermal_conductivity=0.05,
            thermal_emissivity=0.933,
            exposed_area=0.6,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.12, 0]))
)

mml.add_entry(
    m.Material("Lid", True, ID="Lid")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=1.3,
            mass_density=4.0,
            solar_absorption=0.7,
            thermal_conductivity=0.05,
            thermal_emissivity=0.933,
            exposed_area=0.6,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.12, 0]))
)

mml.add_entry(
    m.Material("Glass", True, ID="Glass")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.753,
            mass_density=1.0,
            solar_absorption=0.5,
            thermal_conductivity=1.15,
            thermal_emissivity=0.89,
            exposed_area=0.99,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.04, 0]))
)

mml.add_entry(
    m.Material("WindowGlass", True, ID="WindowGlass")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.753,
            mass_density=1.0,
            solar_absorption=0.5,
            thermal_conductivity=1.15,
            thermal_emissivity=0.89,
            exposed_area=0.99,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.04, 0]))
)

mml.add_entry(
    m.Material("SolarCell", True, ID="SolarCell")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.753,
            mass_density=1.0,
            solar_absorption=0.5,
            thermal_conductivity=1.15,
            thermal_emissivity=0.89,
            exposed_area=0.99,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.04, 0]))
)

mml.add_entry(
    m.Material("Metal", True, ID="Metal")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Gable", True, ID="Gable")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("GableBeam", True, ID="GableBeam")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("WindowFrame", True, ID="WindowFrame")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("WindowSill", True, ID="WindowSill")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("RoofPipe", True, ID="RoofPipe")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("SolarPanel", True, ID="SolarPanel")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Railing", True, ID="Railing")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Gutter", True, ID="Gutter")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Container", True, ID="Container")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Dumpster", True, ID="Dumpster")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Sign", True, ID="Sign")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("SignPost", True, ID="SignPost")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.44,
            mass_density=4.0,
            solar_absorption=0.95,
            thermal_conductivity=30.2,
            thermal_emissivity=0.4,
            exposed_area=0.8,
            thickness=1,
        )
    )
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.08, 0]))
)

mml.add_entry(
    m.Material("Bulb", True, ID="Bulb")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .add_surface_properties(m.WardBrdfSurfaceProperty([0.05, 0.05], [0.18, 0]))
)

concrete_r = np.loadtxt(curve_path / "concrete_00.txt")

mml.add_entry(
    m.Material("Concrete", True, ID="Concrete")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.498,
            mass_density=1.078,
            solar_absorption=0.95,
            thermal_conductivity=20.959,
            thermal_emissivity=0.649,
            exposed_area=0.384,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(concrete_r[:, 0], concrete_r[:, 1])
    )
)

mml.add_entry(
    m.Material("Foundation", True, ID="Foundation")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.498,
            mass_density=1.078,
            solar_absorption=0.95,
            thermal_conductivity=20.959,
            thermal_emissivity=0.649,
            exposed_area=0.384,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(concrete_r[:, 0], concrete_r[:, 1])
    )
)

mml.add_entry(
    m.Material("Mortar", True, ID="Mortar")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.498,
            mass_density=1.078,
            solar_absorption=0.95,
            thermal_conductivity=20.959,
            thermal_emissivity=0.649,
            exposed_area=0.384,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(concrete_r[:, 0], concrete_r[:, 1])
    )
)

rock_r = np.loadtxt(curve_path / "concrete_01.txt")

mml.add_entry(
    m.Material("Rock", True, ID="Rock")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.508,
            mass_density=0.9,
            solar_absorption=0.95,
            thermal_conductivity=18.508,
            thermal_emissivity=0.658,
            exposed_area=0.41,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(rock_r[:, 0], rock_r[:, 1])
    )
)

for pebble_idx in range(5):
    name = "Pebble{:01d}".format(pebble_idx)
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=4.037,
                mass_density=1.242,
                solar_absorption=1,
                thermal_conductivity=0.639,
                thermal_emissivity=0.9,
                exposed_area=-0.492,
                thickness=0.0525,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(rock_r[:, 0], rock_r[:, 1])
        )
    )

wood_r = np.loadtxt(curve_path / "wood.txt")

mml.add_entry(
    m.Material("Wood", True, ID="Wood")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=1.76,
            mass_density=0.9,
            solar_absorption=0.95,
            thermal_conductivity=16.5,
            thermal_emissivity=0.95,
            exposed_area=0.41,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(wood_r[:, 0], wood_r[:, 1])
    )
)

mml.add_entry(
    m.Material("Stick", True, ID="Stick")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=1.76,
            mass_density=0.9,
            solar_absorption=0.95,
            thermal_conductivity=16.5,
            thermal_emissivity=0.95,
            exposed_area=0.41,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(wood_r[:, 0], wood_r[:, 1])
    )
)


road_r = np.loadtxt(curve_path / "asphalt_00.txt")

mml.add_entry(
    m.Material("Road", True, ID="Road")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.21,
            mass_density=0.86,
            solar_absorption=0.95,
            thermal_conductivity=20.03,
            thermal_emissivity=0.640,
            exposed_area=0.327,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(road_r[:, 0], road_r[:, 1])
    )
)

mml.add_entry(
    m.Material("WhiteLine", True, ID="WhiteLine")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.498,
            mass_density=1.078,
            solar_absorption=0.95,
            thermal_conductivity=20.959,
            thermal_emissivity=0.649,
            exposed_area=0.384,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(concrete_r[:, 0], concrete_r[:, 1])
    )
)

mml.add_entry(
    m.Material("YellowLine", True, ID="YellowLine")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.498,
            mass_density=1.078,
            solar_absorption=0.95,
            thermal_conductivity=20.959,
            thermal_emissivity=0.649,
            exposed_area=0.384,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(concrete_r[:, 0], concrete_r[:, 1])
    )
)

brick0_r = np.loadtxt(curve_path / "brick_00.txt")

for brick_idx in range(4):
    name = "Brick{:01d}".format(brick_idx)
    brick_r = np.loadtxt(curve_path / "brick_{:02d}.txt".format(brick_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=4.037,
                mass_density=1.242,
                solar_absorption=1,
                thermal_conductivity=0.639,
                thermal_emissivity=0.9,
                exposed_area=-0.492,
                thickness=0.0525,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(brick_r[:, 0], brick_r[:, 1])
        )
    )

for brick_idx in range(18):
    name = "Brick{:02d}".format(brick_idx)
    brick_r = np.loadtxt(curve_path / "brick_{:02d}.txt".format(brick_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=4.037,
                mass_density=1.242,
                solar_absorption=1,
                thermal_conductivity=0.639,
                thermal_emissivity=0.9,
                exposed_area=-0.492,
                thickness=0.0525,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(brick_r[:, 0], brick_r[:, 1])
        )
    )

for cinder_block_idx in range(8):
    name = "CinderBlock{:02d}".format(cinder_block_idx)
    cinder_block_r = np.loadtxt(curve_path / "cinder_block_{:02d}.txt".format(cinder_block_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=3.965,
                mass_density=1.215,
                solar_absorption=1,
                thermal_conductivity=0.643,
                thermal_emissivity=0.9,
                exposed_area=-0.403,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(cinder_block_r[:, 0], cinder_block_r[:, 1])
        )
    )

grass_r1 = np.loadtxt(curve_path / "grass_01.R.txt")
grass_t1 = np.loadtxt(curve_path / "grass_01.T.txt")

mml.add_entry(
    m.Material("Grass", True, ID="Grass")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.03,
            thermal_conductivity=2.1,
            mass_density=1.05,
            thermal_emissivity=0.98,
            exposed_area=-0.6,
            thickness=0.1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(grass_r1[:, 0], grass_r1[:, 1])
    )
    .add_surface_properties(
        m.SimpleTransmittanceSurfaceProperty(grass_t1[:, 0], grass_t1[:, 1])
    )
)

for grass_idx in range(5):
    name = "Grass{:02d}".format(grass_idx)
    grass_r = np.loadtxt(curve_path / "grass_{:02d}.R.txt".format(grass_idx))
    grass_t = np.loadtxt(curve_path / "grass_{:02d}.T.txt".format(grass_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(grass_r[:, 0], grass_r[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(grass_t[:, 0], grass_t[:, 1])
        )
    )

for gray_shingle_idx in range(12):
    name = "GrayShingle{:02d}".format(gray_shingle_idx)
    gray_shingle_r = np.loadtxt(curve_path / "gray_shingle_{:02d}.txt".format(gray_shingle_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.508,
                mass_density=0.900,
                solar_absorption=0.95,
                thermal_conductivity=18.508,
                thermal_emissivity=0.658,
                exposed_area=-0.410,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(gray_shingle_r[:, 0], gray_shingle_r[:, 1])
        )
    )

leaf_r1 = np.loadtxt(curve_path / "leaf_01.R.txt")
leaf_t1 = np.loadtxt(curve_path / "leaf_01.T.txt")

mml.add_entry(
    m.Material("DeadLeaf", True, ID="DeadLeaf")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(leaf_r1[:, 0], leaf_r1[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(leaf_t1[:, 0], leaf_t1[:, 1])
        )
    )

mml.add_entry(
    m.Material("Leaf", True, ID="Leaf")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(leaf_r1[:, 0], leaf_r1[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(leaf_t1[:, 0], leaf_t1[:, 1])
        )
    )

for leaf_idx in range(5):
    name = "Leaf{:02d}".format(leaf_idx)
    leaf_r = np.loadtxt(curve_path / "leaf_{:02d}.R.txt".format(leaf_idx))
    leaf_t = np.loadtxt(curve_path / "leaf_{:02d}.T.txt".format(leaf_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(leaf_r[:, 0], leaf_r[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(leaf_t[:, 0], leaf_t[:, 1])
        )
    )

mml.add_entry(
    m.Material("Fern", True, ID="Fern")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(leaf_r1[:, 0], leaf_r1[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(leaf_t1[:, 0], leaf_t1[:, 1])
        )
    )

needle_r = np.loadtxt(curve_path / "leaf_01.R.txt")
needle_t = np.loadtxt(curve_path / "leaf_01.T.txt")

mml.add_entry(
    m.Material("Needle", True, ID="Needle")
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.03,
                thermal_conductivity=2.1,
                mass_density=1.05,
                thermal_emissivity=0.98,
                exposed_area=-0.6,
                thickness=0.1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(needle_r[:, 0], needle_r[:, 1])
        )
        .add_surface_properties(
            m.SimpleTransmittanceSurfaceProperty(needle_t[:, 0], needle_t[:, 1])
        )
    )

for red_shingle_idx in range(12):
    name = "RedShingle{:02d}".format(red_shingle_idx)
    red_shingle_r = np.loadtxt(curve_path / "red_shingle_{:02d}.txt".format(red_shingle_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.550,
                mass_density=0.862,
                solar_absorption=0.95,
                thermal_conductivity=19.550,
                thermal_emissivity=0.676,
                exposed_area=-0.320,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(red_shingle_r[:, 0], red_shingle_r[:, 1])
        )
    )

roof00_r = np.loadtxt(curve_path / "asphalt_01.txt")

mml.add_entry(
    m.Material("Roof", True, ID="Roof")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.592,
            mass_density=1.112,
            solar_absorption=0.95,
            thermal_conductivity=20.938,
            thermal_emissivity=0.647,
            exposed_area=-0.400,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(roof00_r[:, 0], roof00_r[:, 1])
    )
)

mml.add_entry(
    m.Material("Roof00", True, ID="Roof00")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.592,
            mass_density=1.112,
            solar_absorption=0.95,
            thermal_conductivity=20.938,
            thermal_emissivity=0.647,
            exposed_area=-0.400,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(roof00_r[:, 0], roof00_r[:, 1])
    )
)

roof01_r = np.loadtxt(curve_path / "asphalt_02.txt")

mml.add_entry(
    m.Material("Roof01", True, ID="Roof01")
    .set_rad_solver(m.SimpleRadiationSolver("LOW"))
    .set_temp_solver(
        m.ThermTempSolver(
            specific_heat=0.531,
            mass_density=0.901,
            solar_absorption=0.95,
            thermal_conductivity=20.938,
            thermal_emissivity=0.658,
            exposed_area=-0.351,
            thickness=1,
        )
    )
    .add_surface_properties(
        m.SimpleReflectanceSurfaceProperty(roof01_r[:, 0], roof01_r[:, 1])
    )
)

for roof_idx in range(2,5):
    name = "Roof{:02d}".format(roof_idx)
    roofs_r = np.loadtxt(curve_path / "gray_shingle_{:02d}.txt".format(roof_idx+5))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.429,
                mass_density=0.820,
                solar_absorption=0.95,
                thermal_conductivity=18.801,
                thermal_emissivity=0.677,
                exposed_area=-0.415,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(roofs_r[:, 0], roofs_r[:, 1])
        )
    )

for roof_idx in range(5):
    name = "Roof{:01d}".format(roof_idx)
    roofs_r = np.loadtxt(curve_path / "gray_shingle_{:02d}.txt".format(roof_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.429,
                mass_density=0.820,
                solar_absorption=0.95,
                thermal_conductivity=18.801,
                thermal_emissivity=0.677,
                exposed_area=-0.415,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(roofs_r[:, 0], roofs_r[:, 1])
        )
    )

for roof_idx in range(4):
    name = "Shingle{:01d}".format(roof_idx)
    roofs_r = np.loadtxt(curve_path / "gray_shingle_{:02d}.txt".format(roof_idx))
    mml.add_entry(
        m.Material(name, True, ID=name)
        .set_rad_solver(m.SimpleRadiationSolver("LOW"))
        .set_temp_solver(
            m.ThermTempSolver(
                specific_heat=0.429,
                mass_density=0.820,
                solar_absorption=0.95,
                thermal_conductivity=18.801,
                thermal_emissivity=0.677,
                exposed_area=-0.415,
                thickness=1,
            )
        )
        .add_surface_properties(
            m.SimpleReflectanceSurfaceProperty(roofs_r[:, 0], roofs_r[:, 1])
        )
    )