# Pose Objects Node

**Description:**
Explicitly sets the location and orientation of one or more objects, with options to translate, rotate, or match terrain slope.

The z-value, altitude, of the translation is relative the the ground at whatevey x and y value is used.

## Inputs
- **Objects**: One or more objects to modify.
- **Translation (m)**: Additive factors to move the object, e.g., [0.0, 0.0, 0.0].
- **Rotation (deg)**: Additive factors to rotate the object, e.g., [0.0, 0.0, 0.0].
- **Match Slope**: Rotate the object to match the slope of the terrain (overrides Rotation).
- **Match Elevation**: Raise the object to match the elevation of the terrain (overrides Translation).

## Outputs
- **Objects**: Objects with updated position.
