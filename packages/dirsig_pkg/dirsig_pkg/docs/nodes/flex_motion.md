# Flex Motion Nodes

> The Flexible Motion Model enhances the capabilities to model moving scene objects and imaging platforms in DIRSIG. The design concept splits calculations into separate location and orientation calculations. This allows for implementing a suite of simpler "engines" for each component, enabling users to configure different scenarios by combining these engines. The nodes are interfaces to the components of the Flexible Motion Model. Read more about the components of the Flexible Motion Model [here](https://dirsig.cis.rit.edu/docs/new/flex_motion.html).

The flex motion node is the primary node used to control the flexible motion model and can be used for objects and sensors in DIRSIG simulations.

# Combined Flex Motion Nodes Summary with Descriptions

## Node: TimeEntry
- **Description**: Captures a timestamped entry for motion control.
- **Inputs**:
  - **Time**: Relative time (seconds) from the beginning of simulation.
  - **Entry**: Location (meters) relative to the origin, or rotation angles (degrees).
- **Outputs**:
  - **Entry**: A timestamped entry.

## Node: WaypointLocationEngine
- **Description**: Manages waypoints to drive object motion over time.
- **Inputs**:
  - **Position(s)**: One or more TimeEntries.
  - **Frame**: Coordinate system, options are "scene" for East-North-Up, "geodetic" for Lat-Lon-Alt, "ecef" for Earth-Centered-Earth-Fixed.
- **Outputs**:
  - **LocationEngine**: A complete LocationEngine object.

## Node: StraightLineLocationEngine
- **Description**: Defines straight-line motion with constant speed and altitude.
- **Inputs**:
  - **Position**: Starting location (meters) relative to the origin.
  - **Speed**: Rate of movement (meters/second).
  - **Heading**: Direction of movement (degrees).
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **LocationEngine**: A complete LocationEngine object.

## Node: FixedLocationEngine
- **Description**: Keeps an object stationary over time.
- **Inputs**:
  - **Position**: Location (meters) relative to the origin.
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **LocationEngine**: A complete LocationEngine object.

## Node: VelocityOrientationEngine
- **Description**: Uses the object's direction of motion to specify orientation. This engine requires a location engine with movement. If paired with a WaypointLocationEngine, ensure that the times in the TimeEntry nodes start from less than zero (-0.1 works fine) and continue till about 0.1 seconds after the Capture Duration field in the DIRSIG5 node to provide sufficient data for velocity calculations and appropriate euler angles.
- **Inputs**:
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **OrientationEngine**: A complete OrientationEngine object.

## Node: EulerOrientationEngine
- **Description**: Uses Euler angles to specify orientation over time.
- **Inputs**:
  - **Orientation(s)**: Time-dependent orientations.
  - **Rotation Order**: Controls the order of rotations.
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **OrientationEngine**: A complete OrientationEngine object.

## Node: LookAtOrientationEngine
- **Description**: Focuses on a specific point or object without defining rotation angles.
- **Inputs**:
  - **LocationEngine**: Any location engine can be used.
  - **Up Vector**: Defines the up-vector of the focal plane.
- **Outputs**:
  - **OrientationEngine**: A complete OrientationEngine object.

## Node: FlexMotion
- **Description**: Combines location and orientation engines for flexible motion modeling. If no LocationEngine is provided then the default configuration is to place the object/sensor at the origin in the ENU frame. If no OrientationEngine is provided then the default configuration is to point towards the +Y-axis.
- **Inputs**:
  - **LocationEngine**: Any location engine will work. If none are provided, the sensor will be placed at the origin.
  - **OrientationEngine**: Any orientation engine will work. If none are provided, the sensor will "look at" the origin.
- **Outputs**:
  - **Motion**: A complete motion object.