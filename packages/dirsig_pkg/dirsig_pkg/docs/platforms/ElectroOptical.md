# Electro-optical Sensor

This node simulates a panchromatic electro-optical sensor derived from the MicaSense Altum-PT platform. It captures a single broadband panchromatic channel, making it suitable for high-throughput imaging tasks where multispectral data is not required.

## Bands

The sensor simulates a single panchromatic band:

- **Panchromatic (PAN):**
  - Pan (403 - 866 nm)

## Inputs

- **`Resolution`**: Sets the resolution of the detector array. It is specified as a list of two integers: `[width, height]`.

- **`Override Focal Length (mm)`**: An optional parameter to override the default focal length. When set to `0.0`, the default focal length of `8.2` mm is used. Any other value is applied directly without modification.

- **`Mount Orientation`**: Controls the sensor mount orientation with two options:
  - `Down` (default): Nadir viewing with rotation angles (0,0,0) - sensor points straight down.
  - `Forward`: Forward-looking with rotation angles (90,0,0) - sensor points forward in the direction of travel.

- **`Collect Truth`**: A boolean toggle to control truth mask generation.
  - `True` (default): Generates an Intersection truth collection alongside the radiance image.
  - `False`: Disables truth collection, reducing simulation time and output size.

- **`Flex Motion`**: An input that accepts a connection from a motion-defining node (e.g., `Static` or `Wiggle`). This defines the motion and orientation of the sensor during the simulation.

- **`Detector Clock Rate (Hz)`**: Sets the clock rate for the detector array, which determines the frame rate.

- **`File Schedule`**: Controls how output image files are generated.
  - `simulation`: A single file for the entire simulation.
  - `task`: An individual file for each task.
  - `capture`: An individual file for each capture in each task.

## Detector Array

The sensor is configured with the following detector array properties:

- **Pixel Pitch**: `3.45` microns.
- **Focal Length**: `8.2` mm (default). Can be overridden via the `Override Focal Length (mm)` input.
- **Ground Sample Distance (GSD)**: At 100 meters altitude, the GSD is approximately 4.21 cm.

## Outputs

- **`Sensor`**: A DIRSIG platform sensor object that can be passed to a renderer.
