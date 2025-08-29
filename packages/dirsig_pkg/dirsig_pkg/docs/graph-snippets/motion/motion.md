# Motion 

> Motion nodes are used to control the position and orientation of an object in DIRSIG. Motion is controlled by the flex motion node which is configured using a location engine and an orientation engine. Each of the engines are detailed in the [Flex Motion Nodes](../nodes/flex_motion.md) section.

## FlexMotion-Euler-North-Nadir.yaml

- [FlexMotion-Euler-North-Nadir.yaml](FlexMotion-Euler-North-Nadir.yaml): Moving North at 7500m/s for 0.05 seconds at an altitude of 300km; looking at the Nadir. The motion starts at the cener of the scene with respect to East and West (x=0) and at a location of 175m South of the center of the scene (y=-175). The object is at an altitude of 300km.

The speed is manifested as the difference of the distance between the time entries that are linked to the waypoint location engine divided by the time difference between the entries.

The orientation is set as a fixed rotation looking straight down.
## Optional

- [Flexible Motion Model](https://dirsig.cis.rit.edu/docs/new/flex_motion.html): DIRSIG's source documentaion for the Flex Motion Model.
