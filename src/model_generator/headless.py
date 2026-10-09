
import sys

from PySide6.QtCore import QCoreApplication

from model_generator.settings.general import set_applications_settings, setup_marker_maps_dir
from model_generator.settings.logging import logger, initialise_logger


def run(args):
    app = QCoreApplication(sys.argv)
    set_applications_settings(app)
    setup_marker_maps_dir()

    initialise_logger()

    logger.info(f"Static trial: {args.trial}")
