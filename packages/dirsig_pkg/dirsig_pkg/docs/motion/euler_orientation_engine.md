## Euler Orientation Engine Node
> Allows the user to specify orientation using Euler angles as a function of time.

- **Inputs**:
  - **Orientation(s)**: One or more TimeEntries where each represents a time-dependent orientation. Uses radians for "scene" coordinate system.
  - **Rotation Order**: Controls the order of how objects are rotated. Options are "xyz", "xzy", "yxz", "yzx", "zxy", "zyx".
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **OrientationEngine**: A complete OrientationEngine object.
