TODO Open Source
- The package volume needs to be shared w/o write permissions, but should be readable by developers for inspection (Read not View)
- Add licensing and link below


# Ana
Ana is the code framework for running jobs in Rendered.ai, a Platform as a Service (PaaS) for generating synthetic data 
that enables data scientists and engineers to overcome the costs and challenges of acquiring and using real data for 
training machine learning and artificial intelligence systems. Rendered.ai has open sourced Ana because it is the 
basis for creating custom channels to generate specific types of synthetic datasets.

Channels contain configuration and customization for the sensor models, platform models, 
and scene content that are used to generate a wide range of simulated sensor outputs that are grouped into a 
synthetic dataset. Developers use Ana to build and test channels, deploy channels to the Rendered.ai engine,
and then use Rendered.ai either through the web interface or through automated API calls to generate datasets 
that can be used for AI/ML training, validation, and testing.

For more information on the Rendered.ai platform and why synthetic data is important for AI, visit 
[the Rendered.ai support pages](https://support.rendered.ai/).

The source code and files in this repository are copyright 2019-2022 DADoES, Inc. and licensed under the Apache 2.0
license which is located at the root level of this repository: [LICENSE](LICENSE).

## Setup
[Setting up your Local Environment](https://support.rendered.ai/development-guides/setting-up-the-development-environment):
Rendered.ai provides Development Docker Images that can simplify setting up your environment for channel development
and can accelerate the channel deployment process.
A development container ([VSCode extension](https://code.visualstudio.com/docs/remote/containers))
saves you the trouble of building the channel every time you want to test,
and ensures the code you are working with is the code that is in the docker when it is registered.

## Running Ana From the Command Line
For convenience during developing a channel, Ana can be run locally from the command line.
To run a graph in a channel a single time use the following command line syntax:
```
ana --graph graphs/default.yaml
```


After running a graph in the channel, an output folder will be created with the following directories:
```
images/
annotations/
metadata/
```

## Preview Mode
Running `ana` with the `--preview` flag will mimic the simulations of the Rendered.ai preview service.
This can be useful to quickly run DIRSIG5 while testing parts of the channel.

When a graph is run in preview mode the convergence parameters are minimized, no annotations are written, and a single frame is generated regardless of the sensor clock.

## Package
The specific logic for this channel is stored in Python packages.
These are are listed in the channel.yml file where you will see the private packages can be found in the packages/ directory.

## Additional Resources
[Ana Software Architecture](https://support.rendered.ai/development-guides/ana-software-architecture) <br />
[Managing Content with Package Volumes](https://support.rendered.ai/development-guides/ana-software-architecture/package-volumes) <br />
[Deploying a Channel](https://support.rendered.ai/development-guides/deploying-a-channel) <br />
[Toybox Examplel](https://support.rendered.ai/development-guides/an-example-channel-toybox/run-and-deploy-the-toybox-channel) <br />
