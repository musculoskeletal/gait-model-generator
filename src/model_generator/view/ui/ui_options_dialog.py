# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_OptionsDialog(object):
    def setupUi(self, OptionsDialog):
        if not OptionsDialog.objectName():
            OptionsDialog.setObjectName(u"OptionsDialog")
        OptionsDialog.resize(450, 206)
        self.verticalLayout = QVBoxLayout(OptionsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(OptionsDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.labelInputDirectory = QLabel(self.groupBox_3)
        self.labelInputDirectory.setObjectName(u"labelInputDirectory")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelInputDirectory)

        self.labelOutputDirectory = QLabel(self.groupBox_3)
        self.labelOutputDirectory.setObjectName(u"labelOutputDirectory")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelOutputDirectory)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEditRootOutput = QLineEdit(self.groupBox_3)
        self.lineEditRootOutput.setObjectName(u"lineEditRootOutput")

        self.horizontalLayout.addWidget(self.lineEditRootOutput)

        self.pushButtonRootOutputChooser = QPushButton(self.groupBox_3)
        self.pushButtonRootOutputChooser.setObjectName(u"pushButtonRootOutputChooser")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonRootOutputChooser.sizePolicy().hasHeightForWidth())
        self.pushButtonRootOutputChooser.setSizePolicy(sizePolicy)
        self.pushButtonRootOutputChooser.setStyleSheet(u"padding: 3px 8px;")

        self.horizontalLayout.addWidget(self.pushButtonRootOutputChooser)


        self.formLayout_3.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEditRootInput = QLineEdit(self.groupBox_3)
        self.lineEditRootInput.setObjectName(u"lineEditRootInput")

        self.horizontalLayout_2.addWidget(self.lineEditRootInput)

        self.pushButtonRootInputChooser = QPushButton(self.groupBox_3)
        self.pushButtonRootInputChooser.setObjectName(u"pushButtonRootInputChooser")
        sizePolicy.setHeightForWidth(self.pushButtonRootInputChooser.sizePolicy().hasHeightForWidth())
        self.pushButtonRootInputChooser.setSizePolicy(sizePolicy)
        self.pushButtonRootInputChooser.setStyleSheet(u"padding: 3px 8px;")

        self.horizontalLayout_2.addWidget(self.pushButtonRootInputChooser)


        self.formLayout_3.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_6 = QGroupBox(OptionsDialog)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.checkBoxApproximateAnthropometrics = QCheckBox(self.groupBox_6)
        self.checkBoxApproximateAnthropometrics.setObjectName(u"checkBoxApproximateAnthropometrics")

        self.verticalLayout_3.addWidget(self.checkBoxApproximateAnthropometrics)


        self.verticalLayout.addWidget(self.groupBox_6)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButtonOK = QPushButton(OptionsDialog)
        self.pushButtonOK.setObjectName(u"pushButtonOK")

        self.horizontalLayout_3.addWidget(self.pushButtonOK)

        self.pushButtonCancel = QPushButton(OptionsDialog)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.horizontalLayout_3.addWidget(self.pushButtonCancel)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(OptionsDialog)
        self.pushButtonOK.clicked.connect(OptionsDialog.accept)
        self.pushButtonCancel.clicked.connect(OptionsDialog.reject)

        QMetaObject.connectSlotsByName(OptionsDialog)
    # setupUi

    def retranslateUi(self, OptionsDialog):
        OptionsDialog.setWindowTitle(QCoreApplication.translate("OptionsDialog", u"Options", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("OptionsDialog", u"File", None))
        self.labelInputDirectory.setText(QCoreApplication.translate("OptionsDialog", u"Input Data Directory:", None))
        self.labelOutputDirectory.setText(QCoreApplication.translate("OptionsDialog", u"Output Data Directory:", None))
        self.pushButtonRootOutputChooser.setText(QCoreApplication.translate("OptionsDialog", u"...", None))
        self.pushButtonRootInputChooser.setText(QCoreApplication.translate("OptionsDialog", u"...", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("OptionsDialog", u"Anthropometrics", None))
        self.checkBoxApproximateAnthropometrics.setText(QCoreApplication.translate("OptionsDialog", u"Approximate missing anthropometrics", None))
        self.pushButtonOK.setText(QCoreApplication.translate("OptionsDialog", u"OK", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("OptionsDialog", u"Cancel", None))
    # retranslateUi

