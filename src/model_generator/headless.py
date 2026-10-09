
import sys

from PySide6.QtCore import QCoreApplication

from c3d_parser.core.c3d_parser import extract_static_data

from model_generator.settings.general import set_applications_settings, setup_marker_maps_dir
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


def run(args):
    app = QCoreApplication(sys.argv)
    set_applications_settings(app)
    setup_marker_maps_dir()

    initialise_logger()

    logger.info(f"Static trial: {args.trial}")

    # Read subject values from the C3D file, overwritten by any command line values.
    c3d_data = extract_static_data(args.trial)
    static_data = {}
    for key, model_key in subject_keys.items():
        value = getattr(args, key)
        static_data[model_key] = value if value is not None else c3d_data.get(key)
