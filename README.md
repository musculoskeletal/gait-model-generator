# Model-Fitter

The Model-Fitter is a Python desktop application for gait analysis.

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


## Feature Requests and Bug Reports

If you would like to suggest a new feature for this application or report a bug you have discovered, please create a
"New Issue" using the appropriate template found in this repository's 
[_Issues_](https://github.com/tsalemink/Model-Fitter/issues) page. Please check that your request does not match any 
existing issues.
