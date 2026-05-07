A configurable RGB sensor that allows customization of key parameters:

Adjustable resolution with configurable pixel count in both dimensions;

Customizable pixel pitch (size and spacing) in microns;

Configurable focal length in millimeters;

Configurable mount orientation with two options:
- Down (default): Nadir viewing with rotation angles (0,0,0) - sensor points straight down
- Forward: Forward-looking with rotation angles (90,0,0) - sensor points forward in the direction of travel

Configurable detector clock rate (Hz) that determines the sensor frame rate;

File schedule control for simulation output with three modes:
- simulation: creates a single file for the entire simulation run
- task: creates an individual file for each task
- capture: creates an individual file for each frame captured

Customizable truth bands through a comma-separated list (defaults to "GeoLocation,Intersection"). You can specify any valid truth band from the DIRSIG truth collection options listed at https://dirsig.cis.rit.edu/docs/new/truth.html, such as Material, Shadow, Temperature, and others;

Supports flexible motion through the Flex Motion input;

Ideal for simulating custom camera systems where specific sensor characteristics are required.