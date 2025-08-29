## Velocity Orientation Engine Node
> Uses the object's direction of motion to specify orientation. This engine requires a location engine with movement. If paired with a WaypointLocationEngine, ensure that the times in the TimeEntry nodes start from less than zero (-0.1 works fine) and continue till about 0.1 seconds after the Capture Duration field in the DIRSIG5 node to provide sufficient data for velocity calculations and appropriate euler angles.

- **Outputs**:
  - **OrientationEngine**: An OrientationEngine object.
