## Straight Line Location Engine Node
> Defines straight-line motion with constant speed and altitude.
- **Inputs**:
  - **Position**: The starting location in meters relative to the origin, establishing the initial point of motion.
  - **Speed**: The rate of movement in meters per second, dictating how fast the object travels.
  - **Heading**: The direction of movement in degrees, determining the trajectory path.
  - **Frame**: Specifies the coordinate system for the position. Options are "scene", "geodetic", and "ecef".
- **Outputs**:
  - **LocationEngine**: A LocationEngine object.
