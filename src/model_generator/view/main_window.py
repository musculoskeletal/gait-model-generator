
import os

from PySide6.QtGui import QColor
from PySide6.QtCore import QSettings, QThread, Signal, QObject
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem,
                               QComboBox)
from pyvistaqt import QtInteractor
from ll_visualiser.visualiser import visualise_model

from c3d_parser.core.c3d_parser import (extract_static_data, extract_marker_names, CancelException,
    approximate_anthropometrics, height_to_mm)

from model_generator.core.generator import generate_model

from model_generator.settings.general import (APPLICATION_NAME, VERSION, DEFAULT_STYLE_SHEET, INVALID_STYLE_SHEET,
                                              get_marker_maps_dir, output_directory_name)
from c3d_parser.view.dialogs.marker_set_dialog import MarkerSetDialog
from c3d_parser.view.dialogs.delete_marker_set_dialog import DeleteMarkerSetDialog

from model_generator.view.ui.ui_main_window import Ui_MainWindow
from model_generator.view.dialogs.options_dialog import OptionsDialog
from model_generator.view.dialogs.about_dialog import AboutDialog
from model_generator.view.utils import handle_runtime_error
from model_generator.settings.logging import logger, log_colours


class _ExecThread(QThread):
    finished = Signal(object)
    cancelled = Signal(Exception)
    failed = Signal(Exception)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            output = self.func(*self.args, **self.kwargs)
            self.finished.emit(output)
        except CancelException as e:
            self.cancelled.emit(e)
        except Exception as e:
            self.failed.emit(e)


class ProgressTracker(QObject):
    progress = Signal(str, str)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.setWindowTitle(f"{APPLICATION_NAME} {VERSION}")

        # Initialise user settings.
        self._input_data_directory = ''
        self._output_data_directory = ''
        self._approximate_anthropometrics = False

        self._disable_spin_box_scrolling()
        self._setup_combo_boxes()
        self._make_connections()
        self._load_settings()
        self._setup_progress_bar()
        self._validate_directory()
        self._setup_visualiser()
        self._setup_log_tab()

    def _setup_progress_bar(self):
        self._progress_value = 0
        self._ui.progressBar.setVisible(False)

    def _setup_visualiser(self):
        self._plotter = QtInteractor(self._ui.tabVisualiser)
        self._plotter.set_background('#2b2b2b')
        self._ui.tabVisualiser.layout().addWidget(self._plotter.interactor)

    def _setup_log_tab(self):
        logger.emitter.log_received.connect(self._write_log)
        self._ui.checkBoxSuppressWarnings.stateChanged.connect(self._filter_log)

    def _write_log(self, date, time, level, message):
        row = self._ui.tableLog.rowCount()
        suppress = self._ui.checkBoxSuppressWarnings.isChecked()

        self._ui.tableLog.insertRow(row)
        colour = log_colours.get(level, QColor(255, 255, 255))
        for column, text in enumerate([date, time, level, message]):
            item = QTableWidgetItem(text)
            item.setBackground(colour)
            self._ui.tableLog.setItem(row, column, item)
        self._ui.tableLog.setRowHidden(row, suppress and level == 'WARNING')
        self._ui.tableLog.scrollToBottom()

    def _filter_log(self):
        suppress = self._ui.checkBoxSuppressWarnings.isChecked()
        for row in range(self._ui.tableLog.rowCount()):
            row_level = self._ui.tableLog.item(row, 2).text()
            self._ui.tableLog.setRowHidden(row, suppress and row_level == 'WARNING')

    def _clear_visualiser(self):
        self._plotter.clear_actors()

    def _clear_progress_bar(self):
        self._ui.labelProgress.setText("")
        self._progress_value = 0
        self._ui.progressBar.setValue(0)

    def _setup_combo_boxes(self):
        self._reset_lab_combo_box()

        # Force Qt to use placeholder text until sex selected.
        self._ui.comboBoxSex.setCurrentIndex(-1)

        self._ui.comboBoxLab.wheelEvent = lambda event: None
        self._ui.comboBoxSex.wheelEvent = lambda event: None

    def _disable_spin_box_scrolling(self):
        self._ui.spinBoxAge.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxHeight.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxBodyMass.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxASISWidth.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxLeftKneeWidth.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxRightKneeWidth.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxLeftAnkleWidth.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxRightAnkleWidth.wheelEvent = lambda event: None
        self._ui.doubleSpinBoxMarkerDiameter.wheelEvent = lambda event: None

    def _reset_lab_combo_box(self):
        current_selection = self._ui.comboBoxLab.currentText()
        marker_maps_dir = get_marker_maps_dir()
        labs = [os.path.splitext(lab)[0] for lab in os.listdir(marker_maps_dir)]
        self._ui.comboBoxLab.clear()
        self._ui.comboBoxLab.addItems(labs)

        if current_selection in labs:
            index = labs.index(current_selection)
            self._ui.comboBoxLab.setCurrentIndex(index)

    def _make_connections(self):
        self._ui.lineEditInputTrial.textChanged.connect(self._validate_input_trial)
        self._ui.lineEditOutputDirectory.textChanged.connect(self._validate_directory)
        self._ui.pushButtonInputTrialChooser.clicked.connect(self._open_input_trial_chooser)
        self._ui.pushButtonOutputDirectoryChooser.clicked.connect(self._open_output_directory_chooser)
        self._ui.pushButtonParseData.clicked.connect(self._parse_c3d_data)
        self._ui.actionQuit.triggered.connect(self._quit_application)
        self._ui.actionReloadInput.triggered.connect(self._validate_input_trial)
        self._ui.actionOptions.triggered.connect(self._show_options_dialog)
        self._ui.actionCustomMarkerSet.triggered.connect(self._show_custom_marker_set_dialog)
        self._ui.actionDeleteMarkerSet.triggered.connect(self._show_delete_marker_set_dialog)
        self._ui.actionAbout.triggered.connect(self._show_about_dialog)

    def _validate_input_trial(self):
        trial_valid = self._validate_directory()

        if trial_valid:
            self._update_subject_info()
            self._clear_visualiser()
        else:
            self._clear_subject_info()

    def _validate_directory(self):
        input_trial = self._ui.lineEditInputTrial.text()
        input_trial_valid = len(input_trial) and os.path.isfile(input_trial) and input_trial.lower().endswith('.c3d')
        self._ui.lineEditInputTrial.setStyleSheet(DEFAULT_STYLE_SHEET if input_trial_valid else INVALID_STYLE_SHEET)

        output_directory = self._ui.lineEditOutputDirectory.text()
        output_directory_valid = len(output_directory) and os.path.isdir(output_directory)
        self._ui.lineEditOutputDirectory.setStyleSheet(DEFAULT_STYLE_SHEET if output_directory_valid else INVALID_STYLE_SHEET)

        self._ui.pushButtonParseData.setEnabled(input_trial_valid and output_directory_valid)

        return input_trial_valid

    def _open_input_trial_chooser(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Static Trial', self._input_data_directory, 'C3D Files (*.c3d)')

        if file_path:
            self._ui.lineEditInputTrial.setText(file_path)
            self._ui.lineEditOutputDirectory.setText(os.path.dirname(file_path))

    def _open_output_directory_chooser(self):
        line_edits = [self._ui.lineEditOutputDirectory]
        self._open_directory_chooser(line_edits, self._output_data_directory)

    def _open_directory_chooser(self, line_edits, data_directory):
        directory = QFileDialog.getExistingDirectory(
            self, 'Select Directory', data_directory)

        if directory:
            for line_edit in line_edits:
                line_edit.setText(directory)

    def _update_subject_info(self):
        static_trial = self._ui.lineEditInputTrial.text()

        self._clear_subject_info()
        self._set_subject_info(static_trial)

        # Fill in any anthropometric gaps.
        if self._approximate_anthropometrics:
            lab = self._ui.comboBoxLab.currentText()
            marker_diameter = self._ui.doubleSpinBoxMarkerDiameter.value()
            anthropometrics = approximate_anthropometrics(os.path.normpath(static_trial), lab, marker_diameter)

            if not self._ui.doubleSpinBoxASISWidth.value():
                self._ui.doubleSpinBoxASISWidth.setValue(anthropometrics['inter_asis_distance'])
            if not self._ui.doubleSpinBoxLeftKneeWidth.value():
                self._ui.doubleSpinBoxLeftKneeWidth.setValue(anthropometrics['left_knee_width'])
            if not self._ui.doubleSpinBoxLeftAnkleWidth.value():
                self._ui.doubleSpinBoxLeftAnkleWidth.setValue(anthropometrics['left_ankle_width'])
            if not self._ui.doubleSpinBoxRightKneeWidth.value():
                self._ui.doubleSpinBoxRightKneeWidth.setValue(anthropometrics['right_knee_width'])
            if not self._ui.doubleSpinBoxRightAnkleWidth.value():
                self._ui.doubleSpinBoxRightAnkleWidth.setValue(anthropometrics['right_ankle_width'])

        # Check height units.
        height = self._ui.doubleSpinBoxHeight.value()
        self._ui.doubleSpinBoxHeight.setValue(height_to_mm(height))

    def _clear_subject_info(self):
        self._ui.comboBoxSex.setCurrentIndex(-1)
        self._ui.spinBoxAge.setValue(0)
        self._ui.doubleSpinBoxHeight.setValue(0)
        self._ui.doubleSpinBoxBodyMass.setValue(0)
        self._ui.doubleSpinBoxASISWidth.setValue(0)
        self._ui.doubleSpinBoxLeftKneeWidth.setValue(0)
        self._ui.doubleSpinBoxRightKneeWidth.setValue(0)
        self._ui.doubleSpinBoxLeftAnkleWidth.setValue(0)
        self._ui.doubleSpinBoxRightAnkleWidth.setValue(0)

    def _set_subject_info(self, c3d_file):
        field_map = {
            'sex': self._ui.comboBoxSex,
            'age': self._ui.spinBoxAge,
            'height': self._ui.doubleSpinBoxHeight,
            'mass': self._ui.doubleSpinBoxBodyMass,
            'asis_width': self._ui.doubleSpinBoxASISWidth,
            'left_knee_width': self._ui.doubleSpinBoxLeftKneeWidth,
            'right_knee_width': self._ui.doubleSpinBoxRightKneeWidth,
            'left_ankle_width': self._ui.doubleSpinBoxLeftAnkleWidth,
            'right_ankle_width': self._ui.doubleSpinBoxRightAnkleWidth,
        }

        static_data = extract_static_data(c3d_file)
        for key, widget in field_map.items():
            value = static_data.get(key)
            if value is not None:
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                else:
                    widget.setValue(value)

    @handle_runtime_error
    def _parse_c3d_data(self):
        static_trial_path = os.path.normpath(self._ui.lineEditInputTrial.text())
        input_directory = os.path.dirname(static_trial_path)
        static_trial = os.path.basename(static_trial_path)

        output_directory = self._ui.lineEditOutputDirectory.text()
        self._output_directory = os.path.normpath(os.path.join(output_directory, output_directory_name))

        if os.path.exists(self._output_directory):
            reply = QMessageBox.warning(self, "Warning",
                                        "The selected output directory already contains results. "
                                        "Do you wish to overwrite these files?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        lab = self._ui.comboBoxLab.currentText()
        marker_diameter = self._ui.doubleSpinBoxMarkerDiameter.value()
        toe_marker_proximal = self._ui.radioButtonProximal.isChecked()
        left_foot_flat = self._ui.checkBoxLeftFootFlat.isChecked()
        right_foot_flat = self._ui.checkBoxRightFootFlat.isChecked()

        static_data = {
            'Sex': self._ui.comboBoxSex.currentText(),
            'Age': self._ui.spinBoxAge.value(),
            'Height': self._ui.doubleSpinBoxHeight.value(),
            'Weight': self._ui.doubleSpinBoxBodyMass.value(),
            'ASIS Width': self._ui.doubleSpinBoxASISWidth.value(),
            'Left Knee Width': self._ui.doubleSpinBoxLeftKneeWidth.value(),
            'Right Knee Width': self._ui.doubleSpinBoxRightKneeWidth.value(),
            'Left Ankle Width': self._ui.doubleSpinBoxLeftAnkleWidth.value(),
            'Right Ankle Width': self._ui.doubleSpinBoxRightAnkleWidth.value(),
        }

        missing = [key for key, value in static_data.items() if not value]
        if missing:
            QMessageBox.warning(self, "Warning", "Subject measurements missing:\n- " + "\n- ".join(missing))
            return

        self._ui.pushButtonParseData.setEnabled(False)

        self._progress_tracker = ProgressTracker()
        self._progress_tracker.progress.connect(self._update_progress)
        self._clear_progress_bar()
        self._ui.progressBar.setVisible(True)

        self._worker = _ExecThread(generate_model, static_trial, input_directory, self._output_directory,
                                   lab, marker_diameter, static_data, left_foot_flat, right_foot_flat,
                                   toe_marker_proximal, self._progress_tracker)
        self._worker.finished.connect(self._parse_finished)
        self._worker.cancelled.connect(self._parse_cancelled)
        self._worker.failed.connect(self._parse_failed)
        self._worker.start()

    @handle_runtime_error
    def _parse_finished(self, model_path):
        self._visualise_model()

        logger.info("Process completed successfully.")
        self._progress_tracker.progress.emit("Process completed successfully", "green")

        self._ui.pushButtonParseData.setEnabled(True)
        self._ui.progressBar.setVisible(False)

    def _parse_cancelled(self, e):
        logger.info(e)
        self._progress_tracker.progress.emit("Completed", "green")

        self._ui.pushButtonParseData.setEnabled(True)
        self._ui.progressBar.setVisible(False)

    @handle_runtime_error
    def _parse_failed(self, e):
        self._progress_tracker.progress.emit("Error encountered", "red")

        self._ui.pushButtonParseData.setEnabled(True)
        self._ui.progressBar.setVisible(False)

        raise e

    def _update_progress(self, message, color):
        self._ui.labelProgress.setText(message)
        self._ui.labelProgress.setStyleSheet(f"color: {color};")

        self._progress_value = min(self._progress_value + 20, 100)
        self._ui.progressBar.setValue(self._progress_value)

    def _visualise_model(self):
        model_directory = os.path.join(self._output_directory, "Models", "Meshes")
        left_original_landmark_file = os.path.join(model_directory, 'original_lms_left.txt')
        right_original_landmark_file = os.path.join(model_directory, 'original_lms_right.txt')
        left_predicted_landmark_file = os.path.join(model_directory, 'predicted_lms_left.txt')
        right_predicted_landmark_file = os.path.join(model_directory, 'predicted_lms_right.txt')
        visualise_model(self._plotter, model_directory, left_original_landmark_file, right_original_landmark_file,
                        left_predicted_landmark_file, right_predicted_landmark_file)

    def _show_options_dialog(self):
        dlg = OptionsDialog(self)
        dlg.load(self._get_options())
        if dlg.exec():
            self._set_options(dlg.save())

    def _get_options(self):
        options = {
            'input_data_directory': self._input_data_directory,
            'output_data_directory': self._output_data_directory,
            'approximate_anthropometrics': self._approximate_anthropometrics,
        }

        return options

    def _set_options(self, options):
        self._input_data_directory = options['input_data_directory']
        self._output_data_directory = options['output_data_directory']
        self._approximate_anthropometrics = options['approximate_anthropometrics']

    def _show_custom_marker_set_dialog(self):
        marker_names = []
        static_trial = self._ui.lineEditInputTrial.text()
        if static_trial and os.path.isfile(static_trial):
            marker_names = extract_marker_names(os.path.normpath(static_trial))

        dlg = MarkerSetDialog(self)
        dlg.set_marker_names(marker_names)
        if dlg.exec():
            dlg.save()
            self._reset_lab_combo_box()

    def _show_delete_marker_set_dialog(self):
        dlg = DeleteMarkerSetDialog(self)
        dlg.setModal(True)
        dlg.error_occurred.connect(self._handle_error)
        dlg.exec()
        self._reset_lab_combo_box()

    def _handle_error(self, e):
        raise e

    def _show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.setModal(True)
        dlg.exec()

    def _save_settings(self):
        settings = QSettings()

        settings.beginGroup('MainWindow')
        settings.setValue('size', self.size())
        settings.setValue('pos', self.pos())
        settings.setValue('is_maximized', self.isMaximized())
        settings.setValue('lab', self._ui.comboBoxLab.currentText())
        settings.setValue('marker_diameter', self._ui.doubleSpinBoxMarkerDiameter.value())
        settings.setValue('toe_marker_proximal', self._ui.radioButtonProximal.isChecked())
        settings.setValue('left_foot_flat', self._ui.checkBoxLeftFootFlat.isChecked())
        settings.setValue('right_foot_flat', self._ui.checkBoxRightFootFlat.isChecked())
        settings.endGroup()

        settings.beginGroup('Options')
        settings.setValue('input_data_directory', self._input_data_directory)
        settings.setValue('output_data_directory', self._output_data_directory)
        settings.setValue('approximate_anthropometrics', self._approximate_anthropometrics)
        settings.endGroup()

    def _load_settings(self):
        settings = QSettings()

        settings.beginGroup('MainWindow')
        if settings.contains('size'):
            self.resize(settings.value('size'))
        if settings.contains('pos'):
            pos = settings.value('pos')
            if pos.x() >= 0 and pos.y() >= 0:
                self.move(pos)
        if settings.contains('is_maximized'):
            if settings.value('is_maximized', 'true') == 'true':
                self.showMaximized()
        if settings.contains('lab'):
            self._ui.comboBoxLab.setCurrentText(settings.value('lab'))
        if settings.contains('marker_diameter'):
            self._ui.doubleSpinBoxMarkerDiameter.setValue(float(settings.value('marker_diameter')))
        if settings.contains('toe_marker_proximal'):
            proximal = settings.value('toe_marker_proximal') == 'true'
            self._ui.radioButtonProximal.setChecked(proximal)
            self._ui.radioButtonMetHead.setChecked(not proximal)
        if settings.contains('left_foot_flat'):
            self._ui.checkBoxLeftFootFlat.setChecked(settings.value('left_foot_flat') == 'true')
        if settings.contains('right_foot_flat'):
            self._ui.checkBoxRightFootFlat.setChecked(settings.value('right_foot_flat') == 'true')
        settings.endGroup()

        settings.beginGroup('Options')
        if settings.contains('input_data_directory'):
            self._input_data_directory = settings.value('input_data_directory')
        if settings.contains('output_data_directory'):
            self._output_data_directory = settings.value('output_data_directory')
        if settings.contains('approximate_anthropometrics'):
            self._approximate_anthropometrics = settings.value('approximate_anthropometrics') == 'true'
        settings.endGroup()

    def _quit_application(self):
        self._save_settings()
        QApplication.quit()

    def closeEvent(self, event):
        if self.sender() is None:
            self._quit_application()
