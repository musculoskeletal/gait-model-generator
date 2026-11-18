# Model-Generator

The Model-Generator is a Python desktop application for gait analysis.

Given a static C3D motion capture trial, this application generates a personalised OpenSim model
for you to use in the OpenSim toolkit.

The entire process runs locally and offline.


## Input Requirements

To be able to create an OpenSim model from your static C3D file, it must contain either: medial
knee markers; or KAD markers as well as knee-width values in the C3D metadata PROCESSING section
(so that we can calculate virtual positions for the medial markers based on the lateral knee marker
positions).

It is recommended that your static C3D file defines the subject's height and weight in the metadata
PROCESSING section, otherwise you will be prompted for this information.


## Headless Mode

This application also has a headless command line interface (CLI). This is useful for integrating model
creation into your own workflows, or for batch processing.

Run it from your command line with:

```
model_generator_cli headless "<static C3D file>" --lab <lab name>
```

The static C3D file can be given as a full path, or as a path relative to the folder you run the command
from. The lab name is the marker set name, as listed in the GUI.

Any anthropometric values that aren't stored in the C3D metadata must be passed as arguments. For example,
if the C3D file doesn't contain the subject's age and sex:

```
model_generator_cli headless "C:\data\static.c3d" --lab RCH --age 9 --sex f
```

Results are saved to a `model_generator_output` folder next to the C3D file, unless another location is
given with `--output`.

For a full list of the required and optional arguments, run:

```
model_generator_cli headless --help
```


## Feature Requests and Bug Reports

If you would like to suggest a new feature for this application or report a bug you have discovered, please create a
"New Issue" using the appropriate template found in this repository's 
[_Issues_](https://github.com/musculoskeletal/gait-model-generator/issues) page. Please check that your request does not match any 
existing issues.
