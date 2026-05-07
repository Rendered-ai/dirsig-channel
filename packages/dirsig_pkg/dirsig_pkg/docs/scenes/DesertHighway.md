# Desert Highway Scene

High resolution scene 6km X 6km with configurable road surface and vegetation.

## Properties

- **Full spectrum** support
- **Elevation**: Nearly flat terrain
- **Geodetic location**: (39.593 deg, -2.1015 deg, 0 m)

## Configuration

### Road Type
Select the surface type for roads in the scene:
- **Paved** - Asphalt roads with white lane markings
- **Dirt** - Unpaved dirt roads with natural appearance using dirt_micro_no emissivity

### Add Brush
Control whether desert brush vegetation is added to the scene:
- **True** - Include Restio eleocharis and Euclea racemosa brush vegetation
- **False** - Scene without brush
- **<random>** - Randomly decide whether to include brush for each run

### Scene Tiles
Tile the 6 km × 6 km scene to extend the simulated area for wide-FOV sensors
(satellites, high-altitude drones). Perimeter tiles are mirrored copies of the
center tile (no objects); only the center tile carries object placements.

- **1** — Single 6 × 6 km tile (default).
- **3 (N/S)** — Center plus north and south tiles (6 × 18 km).
- **9 (3x3)** — Full 18 × 18 km grid of nine tiles.

Each additional tile compiles to its own DIRSIG scene HDF and is registered at
its world-frame offset. Render time scales roughly with tile count.

## Scene Contents

- Terrain with material gradients (Soil-0000, Soil-0001, Soil-0002)
- Road network
- Dry grass (8 variants)
- Large rocks
- Optional: Desert brush vegetation
