## Fixed Location Engine Node
> Keeps an object stationary over time.
- **Coordinate Types and Fields**: [Coordinate Systems Documentation](https://dirsig.cis.rit.edu/docs/new/coordinates.html)
  - **Scene ENU**: Time, Scene ENU X (meters), Scene ENU Y (meters), Scene ENU Z (meters).
  - **Geodetic**: Time, Latitude (degrees, +North), Longitude (degrees, +East), Altitude (meters above WGS-84 ellipsoid).
  - **ECEF**: Time, ECEF X (meters), ECEF Y (meters), ECEF Z (meters).

- **Inputs**:
  - **Position**: Location in meters relative to the origin.
  - **Frame**: Coordinate system, options are "scene", "geodetic", "ecef".
- **Outputs**:
  - **LocationEngine**: A LocationEngine object.
