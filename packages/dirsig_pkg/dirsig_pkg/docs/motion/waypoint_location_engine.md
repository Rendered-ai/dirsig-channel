## Waypoint Location Engine Node
> The `WaypointLocationEngine` node is designed to manage and interpret waypoints for driving object motion over time. It allows users to define complex motion paths by specifying a series of waypoints that the object will follow. The motion path is determined by the sequence and timing of these waypoints, which can be expressed in various coordinate systems.

- **Coordinate Types and Fields**: [Coordinate Systems Documentation](https://dirsig.cis.rit.edu/docs/new/coordinates.html)
  - **Scene ENU**: Time, Scene ENU X (meters), Scene ENU Y (meters), Scene ENU Z (meters).
  - **Geodetic**: Time, Latitude (degrees, +North), Longitude (degrees, +East), Altitude (meters above WGS-84 ellipsoid).
  - **ECEF**: Time, ECEF X (meters), ECEF Y (meters), ECEF Z (meters).

- **Inputs**:
  - **Position(s)**: One or more `TimeEntry` nodes. These entries specify the waypoints for the motion path, with values interpreted according to the selected frame type.
  - **Frame**: The coordinate system for the positions. Options are "scene", "geodetic", "ecef".

- **Outputs**:
  - **LocationEngine**: A LocationEngine object.
