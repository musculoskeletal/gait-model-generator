
import os

from c3d_parser.core.utils import clear_directory
from c3d_parser.core.c3d_parser import parse_static_trial, create_osim_model, validate_static_data

from model_generator.settings.logging import logger


def generate_model(static_trial, input_directory, output_directory, lab, marker_diameter, static_data,
                   left_foot_flat, right_foot_flat, toe_marker_proximal, progress_tracker):
    """
    Generate an OpenSim model according to the static pose and anthropometric information.

    Returns the path of the generated model.
    """
    validate_static_data(static_data)
    clear_directory(output_directory)

    logger.info(f"Generating model from session {os.path.normpath(input_directory)}.")

    static_path = os.path.normpath(os.path.join(input_directory, static_trial))
    static_frame, static_trc, _, _ = parse_static_trial(static_path, lab, marker_diameter, output_directory,
                                                        static_data)

    logger.info("Fitting shape model.")
    model_path = create_osim_model(static_trc, "", static_frame, marker_diameter, static_data, output_directory,
                                   left_foot_flat, right_foot_flat, toe_marker_proximal=toe_marker_proximal,
                                   optimise_knee_axis=False, progress_tracker=progress_tracker)

    logger.info(f"Generated model: {os.path.normpath(model_path)}.")

    return model_path
