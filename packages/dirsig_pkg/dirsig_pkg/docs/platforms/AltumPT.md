# Altum-PT Sensor

This node simulates the MicaSense Altum-PT sensor, a 6-band imaging system that includes five multispectral bands and one panchromatic band.

## Bands

The sensor simulates the following bands:

- **Multispectral (MSI):**
  - Blue (459 - 491 nm)
  - Green (546 - 574 nm)
  - Red (660 - 676 nm)
  - Red Edge (711 - 723 nm)
  - Near-Infrared (NIR) (813 - 871 nm)

- **Panchromatic (PAN):**
  - Pan (403 - 866 nm)

## Inputs

- **`Resolution`**: Sets the resolution of the detector array for all bands. It is specified as a list of two integers: `[width, height]`.

- **`RGB Only`**: A boolean toggle that controls which multispectral bands are simulated.
  - `True`: Simulates only the **Blue**, **Green**, and **Red** bands. The panchromatic sensor is not included.
  - `False`: Simulates all five multispectral bands (Blue, Green, Red, Red Edge, and NIR). The panchromatic sensor is only included if `Add PAN` is set to `True`.

- **`Add PAN`**: A boolean toggle to include the high-resolution panchromatic sensor. This is only effective when `RGB Only` is `False`.

- **`Override Focal Length (mm)`**: An optional parameter to override the default focal lengths. When specified, this value is used for the MSI bands, and the PAN band focal length is automatically set to double this value. Leave empty to use the default focal lengths (8.0 mm for MSI, 16.4 mm for PAN).

- **`Mount Orientation`**: Controls the sensor mount orientation with two options:
  - `Down` (default): Nadir viewing with rotation angles (0,0,0) - sensor points straight down
  - `Forward`: Forward-looking with rotation angles (90,0,0) - sensor points forward in the direction of travel

- **`Flex Motion`**: An input that accepts a connection from a motion-defining node (e.g., `Static` or `Wiggle`). This defines the motion and orientation of the sensor during the simulation.

- **`Detector Clock Rate (Hz)`**: Sets the clock rate for the detector array, which determines the frame rate.

- **`File Schedule`**: Controls how output image files are generated.
  - `simulation`: A single file for the entire simulation.
  - `task`: An individual file for each task.
  - `capture`: An individual file for each capture in each task.

## Detector Array

The sensor is configured with the following detector array properties:

- **Pixel Pitch**: `3.45` microns for both MSI and PAN sensors.
- **Focal Length**: `8.0` mm for MSI sensor and `16.4` mm for PAN sensor.
- **Ground Sample Distance (GSD)**: At 100 meters distance, the GSD is approximately 4.31 cm for MSI and 2.10 cm for PAN.
- **Resolution**: The PAN sensor's resolution is twice that of the MSI sensor's resolution in both width and height.

## Outputs

- **`Sensor`**: A DIRSIG platform sensor object that can be passed to a renderer.
