
import os
import sys
import traceback

from PySide6.QtCore import QCoreApplication

from c3d_parser.core.c3d_parser import extract_static_data, approximate_anthropometrics, ParserError

from model_generator.core.generator import generate_model
from model_generator.settings.general import set_applications_settings, setup_marker_maps_dir, output_directory_name
from model_generator.settings.logging import logger, initialise_logger


subject_keys = {
    'sex': 'Sex',
    'age': 'Age',
    'height': 'Height',
    'mass': 'Weight',
    'asis_width': 'ASIS Width',
    'left_knee_width': 'Left Knee Width',
    'right_knee_width': 'Right Knee Width',
    'left_ankle_width': 'Left Ankle Width',
    'right_ankle_width': 'Right Ankle Width',
}

approximation_keys = {
    'inter_asis_distance': 'ASIS Width',
    'left_knee_width': 'Left Knee Width',
    'right_knee_width': 'Right Knee Width',
    'left_ankle_width': 'Left Ankle Width',
    'right_ankle_width': 'Right Ankle Width',
}


def run(args):
    app = QCoreApplication(sys.argv)
    set_applications_settings(app)
    setup_marker_maps_dir()

    initialise_logger()

    logger.info(f"Static trial: {args.trial}")

    output_directory = os.path.normpath(os.path.join(args.output or os.path.dirname(args.trial),
                                                     output_directory_name))
    if os.path.exists(output_directory) and not args.overwrite:
        logger.error(f"The output directory already contains results: {output_directory}. "
                     f"Use --overwrite to replace them.")
        return 1

    # Read subject values from the C3D file, overwritten by any command line values.
    c3d_data = extract_static_data(args.trial)
    static_data = {}
    for key, model_key in subject_keys.items():
        value = getattr(args, key)
        static_data[model_key] = value if value is not None else c3d_data.get(key)

    # Fill any gaps with values approximated from the marker data.
    if args.approximate_anthropometrics:
        anthropometrics = approximate_anthropometrics(args.trial, args.lab, args.marker_diameter)
        for key, model_key in approximation_keys.items():
            if not static_data[model_key]:
                static_data[model_key] = anthropometrics[key]

    static_trial_path = os.path.normpath(args.trial)
    try:
        generate_model(os.path.basename(static_trial_path), os.path.dirname(static_trial_path), output_directory,
                       args.lab, args.marker_diameter, static_data, args.left_foot_flat, args.right_foot_flat,
                       args.toe_marker_proximal, None)
    except ParserError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error(f'Unexpected error: {e}\n{traceback.format_exc()}')
        return 1
