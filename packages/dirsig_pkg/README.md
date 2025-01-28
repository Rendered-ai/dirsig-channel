The dirsig package stores nodes and libraries for running dirsig on Rendered.ai

## Package Structure
The content is organized as follows.

- nodes/ - modules for Rendered.ai node schema and logic
- lib/ - utilities required by the nodes
- package.yml - data volume configuration file

## Package Volume Content
The `dirsig-shared` package volume has several directories, one for each scene, and others for object bundles
- The scene content is needed to generate the scene files in the channel
- The Bundle Inventory contains the content shared by DIRS Lab
- The 'Bundles' are custom bundles, e.g. objects for specific demos

## Graph Components
### Objects, Modifiers, and Scenes
Objects are handled by Rendered.ai generators.
For scalability and randomization, generators instance objects as they are needed for each run.
Further, modifiers, like the Random Object Cluster modifier, are generators.
When any generator is triggered (calling its exec() method), it returns an object that has been configured with DIRSIG instances.
Scene nodes can input generators and are responsible for triggering them based on how the user wants to add objects.

All object generators are initialized with a static instance.

Object bundles can be added to a workspace volume. Users can add a File Node for a glist file. These are converted to generators by any node that inputs generators.

The Move Object and Scale Object modifier generators update the static instance properties of their input children generators.

The Random Object Cluster modifier generator is a factory for objects with DIRSIG Static Instance Binary Files.
They are anchored to terrain from the scenes they are called from.
Children objects for cluster modifiers have any other instances removed.

The Dynamize modifier generator is a factory for objects with a DIRSIG Dynamic Instance.
Children objects for these modifiers have any other instances removed.

### Sensors and Platforms
The various sensors are framing array approximations of common imaging products.
These are all coded with the dirsig file manager Python tool.
Parameters are exposed through the channel nodes for either randomization or to set specific sensor properties.

The platform motion can be set up with common location and orientation engines.

### Simulation
The DIRSIG5 node configures the tasks, possibly a custom ephemeris DIRSIG plugin, and runs DIRSIG5.
It uses the input scene, platform, and reference datetime.
This open source channel always uses a basic atmosphere.

The resulting ENVI files are parsed into Rendered.ai's dataset format.
RGB chips are extracted from the simulated values,
and the truth masks are parsed into non-RASTER annotations with metadata.
