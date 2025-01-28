# DIRSIG Imaging Channel
The DIRSIG imaging channel uses the DIRSIG5 radiometric simulation tool with parameterized configuration files. Graphs of this channel are meant to demonstrate dataset creation with several parametric randomizations, such as the location of the center of the image, time of day, atmospheric conditions, and rotation of the platform. The channel comprises a calibration panels scene, an industrial scene, three platforms (Satellite HSI, High Aerial RGB, and Low Aerial Multispectral), and a summer and a winter atmosphere node with various conditions selection.

## Graph Requirements
All graphs must have a Simulate node with input node links of a scene node, an atmosphere node, and a platform node. Everything needed to create a scene is under the Scenes category in the node catalog. Scene nodes can be found in the Backgrounds sub-category, e.g. Industrial Scene and Calibration Panels. The Calibration Panels node requires at least one Panel Cluster which comes from a Panel Cluster node, and this in turn requires a Material.

## Channel Nodes
The following nodes are available in the channel:
| Name | Inputs | Outputs | Description |
|---|---|---|---|
| Ideal Reflectance Material | Reflectance | Material ID | An Ideal Emissivity Curve |
| Calibration Panels | Background Reflectance<br />Panel Clusters | Scene | An Ideal Scene |
| Panel Cluster | Panel Material ID<br />Grid<br />Target Size<br />Spacing<br />Offset | Panel Cluster | A cluster of panels with ideal spectral reflectance curves - Input target size of each square panel edge (meters), spacing distance between each panel (meters), and cluster offset x and y (meters). |
| Trona | Scan Center | Scene | High resolution scene of the Trona, CA Borax Plant from RIT (MegaScene2); Input scan center can be the center of the scene or a random location. |
| Harvard Forest | - | Scene | The Harvard forest very high resolution scene from RIT; Input scan center can be the center of the scene or a random location. |
| Lake Tahoe | Scan Center | Scene | Tahoe (low resolution) scene from RIT; Input scan center can be the center of the scene or a random location. |
| MegaScene1 | Scan Center | Scene | MegaScene1 from RIT; Input scan center can be the center of the scene or a random location. |
| Denver | Scan Center | Scene | Low resolution scene of large area around Denver, CO; Input scan center can be the center of the scene or a random location. |
| Basic Atmosphere | - | Atmosphere | DIRSIG Simple Atmosphere Plugin Configuration |
| Summer Atmosphere | Conditions | Atmosphere | DIRSIG FourCurve Atmosphere plugin configuration for mid-latitude Summer conditions - urban/rural aerosols and various visibilities |
| Winter Atmosphere | Conditions | Atmosphere | DIRSIG FourCurve Atmosphere plugin configuration for mid-latitude Winter conditions - urban/rural aerosols and various visibilities |
| Simulate | Scene<br />Atmosphere<br />Platform | - | Render ENVI datacube with DIRSIG5 |
| Medium Resolution EO Platform | Collect Intersection<br />Collect Geolocation | Platform | A simplified 640x480 framing-array approximation of the WorldView 3 9-channel VIS+NIR system (~1.24m GSD). |
| Low Resolution EO Platform | Reference Datetime<br />Collect Intersection<br />Collect Geolocation<br />Collect Shadow | Platform | A simplified 640x480 framing-array approximation of the Planet Super Dove 8-channel VIS+NIR system (~3m GSD). The configuration is a decent approximation of the PS0 and PSB.SD instruments. |
| High Resolution EO Platform | Collect Intersection<br />Collect Geolocation | Platform | A simplified 1024x768 framing-array approximation of the Planet SkySat 16-21 systems with 5-channels PAN+VIS+NIR (~ 75cm GSD). |
| Drone | Look Angle<br />Platform Azimuth<br />Flight Altitude (m)<br />Reference Datetime | Platform | RGB 35mm 1280x720 Camera; 0.5 m GSD at Nadir when flown at 60m. Platform Azimuth input of '<random>' will use an angle bewteen 0 and 360 degrees. Reference Time input of '<random>' will choose a random hour between 7 AM and 6 PM. |
| Airborne HSI Spectrometer | Reference Datetime<br />Flight Altitude (km)<br />Collect Material<br />Collect Intersection<br />Collect Shadow | Platform | A simplified 667x512 framing array approximation of NASA's AVIRIS (Classic) airborne hyperspectral imaging system with 224 channels so the user doesn't need to perform ground processing. Flown with one of two altitudes - 20 km for a U2 (~20m GSD) or 4 km for a Twin Otter (~4m GSD). |
| Random Integer | low<br />high<br />size | out | Generate random integers from low (inclusive) to high (exclusive), see numpy.random.randint for details |
