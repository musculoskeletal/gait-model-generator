
import os

from PySide6.QtWidgets import QDialog, QFileDialog

from model_generator.view.ui.ui_options_dialog import Ui_OptionsDialog
from model_generator.settings.general import DEFAULT_STYLE_SHEET, INVALID_STYLE_SHEET


class OptionsDialog(QDialog):

    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(parent)
        self._ui = Ui_OptionsDialog()
        self._ui.setupUi(self)

        self._disable_default_button_selection()

        self._make_connections()

    def _make_connections(self):
        self._ui.lineEditRootInput.textChanged.connect(self._validate_data_directory)
        self._ui.lineEditRootOutput.textChanged.connect(self._validate_data_directory)
        self._ui.pushButtonRootInputChooser.clicked.connect(self._open_input_directory_chooser)
        self._ui.pushButtonRootOutputChooser.clicked.connect(self._open_output_directory_chooser)

    def _disable_default_button_selection(self):
        self._ui.pushButtonOK.setAutoDefault(False)
        self._ui.pushButtonCancel.setAutoDefault(False)
        self._ui.pushButtonRootInputChooser.setAutoDefault(False)
        self._ui.pushButtonRootOutputChooser.setAutoDefault(False)

    def load(self, options):
        self._ui.lineEditRootInput.setText(options['input_data_directory'])
        self._ui.lineEditRootOutput.setText(options['output_data_directory'])
        self._ui.checkBoxApproximateAnthropometrics.setChecked(options['approximate_anthropometrics'])

    def save(self):
        options = {
            'input_data_directory': self._ui.lineEditRootInput.text(),
            'output_data_directory': self._ui.lineEditRootOutput.text(),
            'approximate_anthropometrics': self._ui.checkBoxApproximateAnthropometrics.isChecked(),
        }

        return options

    def _validate_data_directory(self):
        line_edit = self.sender()
        directory = line_edit.text()
        directory_valid = len(directory) and os.path.isdir(directory)
        line_edit.setStyleSheet(DEFAULT_STYLE_SHEET if directory_valid else INVALID_STYLE_SHEET)

    def _open_input_directory_chooser(self):
        self._open_directory_chooser(self._ui.lineEditRootInput)

    def _open_output_directory_chooser(self):
        self._open_directory_chooser(self._ui.lineEditRootOutput)

    def _open_directory_chooser(self, line_edit):
        current_directory = line_edit.text()
        if not os.path.isdir(current_directory):
            current_directory = ''

        directory = QFileDialog.getExistingDirectory(
            self, 'Select Directory', current_directory)

        if directory:
            line_edit.setText(directory)
