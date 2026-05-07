# DIRSIG Imaging Channel

The DIRSIG Imaging Channel is designed to configure and run simulations using **DIRSIG5 (Digital Imaging and Remote Sensing Image Generation)**, a physics-based radiometric image simulator. Comprehensive documentation for DIRSIG5, including its various models, plugins, and capabilities, can be found at the official [DIRSIG Documentation site](https://dirsig.cis.rit.edu/docs/new/index.html).

This channel provides a curated collection of nodes that abstract and parameterize DIRSIG5 functionalities. Users construct **Graphs** by connecting these nodes to define specific simulation scenarios. These graphs are then used to generate synthetic datasets, often incorporating randomization of parameters (e.g., sensor position, time of day) to create diverse and comprehensive datasets for training and testing algorithms.

## Use Cases

The channel includes example graphs and configurations for several key remote sensing applications:

- **Earth Observation**: Satellite-based imaging scenarios with various orbital parameters and sensor configurations
- **Drone Imagery**: Low-altitude aerial imaging with customizable flight paths and camera settings
- **Thermal IR**: Infrared imaging simulations for both aerial and ground-based thermal detection applications

Each use case leverages DIRSIG's internal models for atmospheric conditions, material properties, and sensor characteristics.

## Graph Requirements
All graphs within this channel must include a `Simulate` node (shown as `DIRSIG5` in the UI). This node serves as the core execution trigger and requires inputs from at least a `Scene` node (defining the environment) and a `Sensor` node (which bundles the platform, its motion, and sensor characteristics).

Atmosphere, weather, and material properties are handled by DIRSIG5 internally. Solar and lunar positioning is configurable via the optional `Ephemeris` input on the `Simulate` node.

Nodes for creating scenes are typically found under the "Scenes" category in the node catalog.

## Channel Nodes
The following nodes are available in the DIRSIG Imaging Channel. Each node is designed to control specific aspects of the DIRSIG5 simulation:

| Name                          | Category   | Subcategory         | Key Inputs (Examples)                                       | Key Outputs (Example) | Description                                                                 |
|-------------------------------|------------|---------------------|-------------------------------------------------------------|-----------------------|-----------------------------------------------------------------------------|
| **Backgrounds**               |            |                     |                                                             |                       |                                                                             |
| Sierra Nevada                 | Scenes     | Backgrounds         | Objects                                                     | Scene                 | Low resolution DIRSIG scene: 150km x 150km.                                 |
| Desert Highway                | Scenes     | Backgrounds         | Objects, Road Type (Paved/Dirt), Add Brush, Scene Tiles ("1" / "3 (N/S)" / "9 (3x3)") | Scene                 | High resolution DIRSIG scene: 6km x 6km per tile. The `Scene Tiles` input mosaics mirrored copies of the center tile to expand coverage for wide-FOV sensors: `1` = single 6x6 km tile, `3 (N/S)` = 6x18 km strip, `9 (3x3)` = 18x18 km block. Only the center tile carries object placements; perimeter tiles are object-free terrain. |
| Urban                         | Scenes     | Backgrounds         | Objects                                                     | Scene                 | High resolution DIRSIG urban scene: 3km X 3km.                              |
| **Ephemeris**                 |            |                     |                                                             |                       |                                                                             |
| Fixed Ephemeris               | Simulators | Ephemeris           | Solar Zenith, Solar Azimuth, Lunar Zenith, Lunar Azimuth...   | Ephemeris             | Directly supply static positions of the Sun and Moon.                       |
| **Motion**                    |            |                     |                                                             |                       |                                                                             |
| TimeEntry                     | Motion     | Common              | Time, Entry (location or rotation)                          | Entry                 | Specifies a location or orientation entry at one time step.                 |
| WaypointLocationEngine        | Motion     | Location Engines    | Position(s) (TimeEntries), Frame                            | LocationEngine        | Drives object motion through a series of waypoints over time.               |
| StraightLineLocationEngine    | Motion     | Location Engines    | Position, Speed, Heading, Frame                             | LocationEngine        | Defines an object moving in a straight line (constant altitude, speed).     |
| FixedLocationEngine           | Motion     | Location Engines    | Position, Frame                                             | LocationEngine        | Defines a static (non-moving) object location.                              |
| VelocityOrientationEngine     | Motion     | Orientation Engines | Frame                                                       | OrientationEngine     | Orients an object based on its direction of motion.                         |
| EulerOrientationEngine        | Motion     | Orientation Engines | Orientation(s) (TimeEntries), Rotation Order, Frame         | OrientationEngine     | Orients an object using Euler angles as a function of time.                 |
| LookAtOrientationEngine       | Motion     | Orientation Engines | LocationEngine (target), Up Vector                          | OrientationEngine     | Orients an object to continuously point at a specified location or another moving object. |
| FlexMotion                    | Motion     | Platform Motion     | LocationEngine, OrientationEngine                           | FlexMotion            | Combines location and orientation engines to define complex platform motion. |
| **Object Modifiers**          |            |                     |                                                             |                       |                                                                             |
| ScaleObjects                  | Scenes     | Object Modifiers    | Objects (link), Scale Factors                               | Objects               | Scales the size of input objects.                                           |
| DynamizeObjects               | Scenes     | Object Modifiers    | Objects (link), Flex Motion (link)                          | Objects               | Applies dynamic motion (location and orientation) to objects.               |
| PoseObjects                   | Scenes     | Object Modifiers    | Objects (link), Translation, Rotation, Match Slope, Match Elevation | Objects               | Explicitly sets the static location and orientation of objects.             |
| ClusterObjects                | Scenes     | Object Modifiers    | Objects (link), Scene Location, Number of Objects, Radius   | Objects               | Places multiple instances of objects in a cluster around a location.        |
| **Object Inventory (Examples)** |        |                     |                                                             |                       |                                                                             |
| Bench                         | Scenes     | Bundle Inventory    | -                                                           | Bench Object          | A simple bench model.                                                       |
| Concrete Barrier              | Scenes     | Bundle Inventory    | -                                                           | Concrete Barrier Obj  | A concrete barrier model.                                                   |
| Drainage Pipe                 | Scenes     | Bundle Inventory    | Type                                                        | Drainage Pipe Obj     | A drainage pipe model with selectable types.                                |
| *Note: ~28 object models are available under "Bundle Inventory", spanning vehicles (B737, generic vehicles, tires), structures (houses, barriers, fuel tanks, transformers, street lights), vegetation (trees, shrubs, hobble bush), targets (Macbeth chart, tri-bar), and miscellaneous props.* |       |                     |                                                             |                       |                                                                             |
| **Platforms/Sensors**         |            |                     |                                                             |                       |                                                                             |
| Medium Resolution EO Platform | Platforms  | Sensors             | Flex Motion (link), Data Collection Flags                   | Sensor                | Approximates WorldView 3 VIS+NIR sensor.                                    |
| Low Resolution EO Platform    | Platforms  | Sensors             | Flex Motion (link), Data Collection Flags                   | Sensor                | Approximates Planet SuperDove VIS+NIR sensor.                               |
| High Resolution EO Platform   | Platforms  | Sensors             | Flex Motion (link), Data Collection Flags                   | Sensor                | Approximates Planet SkySat PAN+VIS+NIR sensor.                              |
| Drone                         | Platforms  | Sensors             | Flex Motion (link), Detector Clock Rate                     | Sensor                | Generic RGB drone camera model (35mm focal length, 1280x720).               |
| Airborne HSI Spectrometer     | Platforms  | Sensors             | Flex Motion (link), Data Collection Flags                   | Sensor                | Approximates NASA's AVIRIS (Classic) airborne hyperspectral imager.         |
| CustomRGBSensor               | Platforms  | Sensors             | Pixels, Pixel Pitch, Focal Length, F-Number, Flex Motion    | Sensor                | A customizable RGB sensor model.                                            |
| Thermal Sensor                | Platforms  | Sensors             | Band Limits, Pixels, Pixel Pitch, Focal Length, Flex Motion | Sensor                | Thermal infrared sensor with configurable parameters.                        |
| **Simulators**                |            |                     |                                                             |                       |                                                                             |
| Simulate (DIRSIG5)            | Simulators | DIRSIG              | Scene (link), Sensor (link), Reference Datetime, Ephemeris  | -                     | Core DIRSIG5 simulation trigger.                                            |

## Common Utility Nodes
In addition to the DIRSIG-specific nodes, this channel includes several general-purpose utility nodes from the anatools package that can be used for parameter generation, randomization, and graph control:

| Node Name                    | Category   | Subcategory         | Key Inputs                                                  | Key Outputs           | Description                                                                 |
|------------------------------|------------|---------------------|-------------------------------------------------------------|----------------------|-----------------------------------------------------------------------------|
| Random Integer               | Common     | Values              | Low, High                                                    | Value                 | Generates random integers within a specified range.                          |
| Random Uniform               | Common     | Values              | Low, High                                                    | Value                 | Generates random floating-point values with uniform distribution.           |
| Random Normal                | Common     | Values              | Mean, Standard Deviation                                     | Value                 | Generates random values with normal (Gaussian) distribution.                |
| Sweep np.arange              | Common     | Values              | Start, Stop, Step                                            | Value                 | Creates evenly spaced values using numpy's arange function.                 |
| Sweep np.linspace            | Common     | Values              | Start, Stop, Num                                             | Value                 | Creates evenly spaced values using numpy's linspace function.               |
| Vector2D                     | Common     | Values              | X, Y                                                         | Vector                | Creates a 2D vector from X and Y components.                                |
| Vector3D                     | Common     | Values              | X, Y, Z                                                      | Vector                | Creates a 3D vector from X, Y, and Z components.                            |
| Weight                       | Common     | Graph Controls      | Value                                                        | -                     | Controls the weight/probability of a branch in the graph.                   |
| Select Generator             | Common     | Graph Controls      | Generators, Weights                                          | Value                 | Selects one of multiple input generators based on weights.                  |
| Datetime                     | Common     | Values              | Year, Month, Day, Hour, Minute, Second                       | Datetime              | Creates a datetime object from individual components.                       |
