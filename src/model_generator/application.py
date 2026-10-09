
import sys
import ctypes
import argparse

from model_generator.settings.general import (APPLICATION_NAME, set_applications_settings,
    application_instance_exists, start_application_server, setup_marker_maps_dir)
from model_generator.settings.logging import initialise_logger, filter_c3d_warnings


def windows_main():
    if sys.platform == 'win32':
        my_app_id = 'Motion_Connect.Model_Generator'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    from model_generator.splashscreen import SplashScreen
    splash = SplashScreen()
    splash.show()

    splash.showMessage("Loading settings ...", 5)
    set_applications_settings(app)
    setup_marker_maps_dir()

    # Prevent multiple application instances.
    if application_instance_exists():
        print("Model-Generator instance is already running.")
        sys.exit(1)
    app_server = start_application_server()

    splash.showMessage('Initialising logger ...', 20)
    initialise_logger()

    splash.showMessage('Importing dependencies ...', 40)
    from model_generator.view.main_window import MainWindow
    splash.showMessage('Creating main window ...', 80)
    window = MainWindow()
    splash.showMessage('Showing main window ...', 90)
    window.show()

    splash.showMessage('Load complete ...', 100)
    splash.finish(window)

    return app.exec()


def sans_gui_main(args):
    from model_generator.headless import run
    return run(args)


def _sex(value):
    sexes = {'f': 'Female', 'female': 'Female', 'm': 'Male', 'male': 'Male'}
    if value.lower() not in sexes:
        raise argparse.ArgumentTypeError(f"invalid choice: '{value}' (choose from female, male, f, m)")
    return sexes[value.lower()]


def _parse_args():
    parser = argparse.ArgumentParser(prog=APPLICATION_NAME)
    subparsers = parser.add_subparsers(dest="command")

    headless_parser = subparsers.add_parser("headless", help="Run Model-Generator in headless mode.")
    headless_parser.add_argument("trial", help="Static trial C3D file.")
    headless_parser.add_argument("--lab", required=True, help="Marker set name.")
    headless_parser.add_argument("--output", help="Output folder (default: input directory).")
    headless_parser.add_argument("--marker-diameter", type=float, default=14.0,
                                 help="Marker diameter in mm (default: %(default)s).")
    headless_parser.add_argument("--left-foot-flat", action=argparse.BooleanOptionalAction, default=True,
                                 help="Left foot flat (default: on).")
    headless_parser.add_argument("--right-foot-flat", action=argparse.BooleanOptionalAction, default=True,
                                 help="Right foot flat (default: on).")
    headless_parser.add_argument("--toe-marker-proximal", action="store_true",
                                 help="Toe markers are proximal (default: 2nd/3rd metatarsal head).")
    headless_parser.add_argument("--approximate-anthropometrics", action="store_true",
                                 help="Approximate missing anthropometrics from marker data.")
    headless_parser.add_argument("--overwrite", action="store_true",
                                 help="Overwrite existing results in the output folder.")

    subject_values = headless_parser.add_argument_group("subject values",
                                                        "Override the values stored in the C3D file.")
    subject_values.add_argument("--sex", type=_sex, help="female, male, f or m (any case).")
    subject_values.add_argument("--age", type=int, help="Age in years.")
    subject_values.add_argument("--height", type=float, help="Height in mm.")
    subject_values.add_argument("--mass", type=float, help="Body mass in kg.")
    subject_values.add_argument("--asis-width", type=float, help="Inter-ASIS distance in mm.")
    subject_values.add_argument("--left-knee-width", type=float, help="Left knee width in mm.")
    subject_values.add_argument("--right-knee-width", type=float, help="Right knee width in mm.")
    subject_values.add_argument("--left-ankle-width", type=float, help="Left ankle width in mm.")
    subject_values.add_argument("--right-ankle-width", type=float, help="Right ankle width in mm.")

    return parser.parse_args()


def main():
    args = _parse_args()
    filter_c3d_warnings()

    if args.command == "headless":
        result = sans_gui_main(args)
    else:
        result = windows_main()

    sys.exit(result)


if __name__ == '__main__':
    main()
