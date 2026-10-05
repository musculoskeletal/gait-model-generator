
import sys
import ctypes

from model_generator.settings.general import (set_applications_settings, application_instance_exists,
    start_application_server, setup_marker_maps_dir)
from model_generator.settings.logging import initialise_logger, filter_c3d_warnings


def main():
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

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
