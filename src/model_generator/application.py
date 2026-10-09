
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
    filter_c3d_warnings()

    splash.showMessage('Importing dependencies ...', 40)
    from model_generator.view.main_window import MainWindow
    splash.showMessage('Creating main window ...', 80)
    window = MainWindow()
    splash.showMessage('Showing main window ...', 90)
    window.show()

    splash.showMessage('Load complete ...', 100)
    splash.finish(window)

    return app.exec()


def sans_gui_main():
    pass


def _parse_args():
    parser = argparse.ArgumentParser(prog=APPLICATION_NAME)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("headless", help="Run Model-Generator in headless mode.")

    return parser.parse_args()


def main():
    args = _parse_args()

    if args.command == "headless":
        result = sans_gui_main()
    else:
        result = windows_main()

    sys.exit(result)


if __name__ == '__main__':
    main()
