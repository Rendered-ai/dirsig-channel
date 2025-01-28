# Velocity Orientation Engine

This engine requires a location engine with movement otherwise an error
will be generated.

If this engine is paired with a WaypointLocationEngine, it is important that the
times in the TimeEntry nodes start from less than zero (-0.1 works fine) and 
continue till about 0.1 seconds after the Capture Duration field in the DIRSIG5
node. This is so that the velocity calculations have enough data to work on and
can thus calculate the appropriate euler angles.