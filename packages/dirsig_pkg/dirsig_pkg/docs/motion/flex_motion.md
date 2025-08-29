# Flex Motion Node

> The Flexible Motion Model enhances the capabilities to model moving scene objects and imaging platforms in DIRSIG. The design concept splits calculations into separate location and orientation calculations. This allows for implementing a suite of simpler "engines" for each component, enabling users to configure different scenarios by combining these engines. The nodes are interfaces to the components of the Flexible Motion Model. Read more about the components of the Flexible Motion Model [here](https://dirsig.cis.rit.edu/docs/new/flex_motion.html).

The flex motion node is the primary node used to control the flexible motion model and can be used for objects and sensors in DIRSIG simulations.

- **Description**: Combines location and orientation engines for flexible motion modeling. If no LocationEngine is provided then the default configuration is to place the object/sensor at the origin in the ENU frame. If no OrientationEngine is provided then the default configuration is to point towards the +Y-axis.
- **Inputs**:
  - **LocationEngine**: Any location engine will work. If none are provided, the sensor will be placed at the origin.
  - **OrientationEngine**: Any orientation engine will work. If none are provided, the sensor will "look at" the origin.
- **Outputs**:
  - **Motion**: A motion model.