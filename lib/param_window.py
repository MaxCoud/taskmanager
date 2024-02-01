from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication, QCursor
from PySide6.QtWidgets import QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDialog, QMessageBox, QComboBox


class ParamDialog(QDialog):

    def __init__(self, main_win):
        super(ParamDialog, self).__init__()

        self.mainWin = main_win

        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Paramètres")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 9.5

        self.modifying = False

        grid = QGridLayout()

        lbl = QLabel("Notifications")
        lbl.setFont(QFont('AnyStyle', self.titleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0, 1, 3)

        lbl = QLabel("Activées")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 1, 0)

        self.notifActivatedCheckBox = QCheckBox()
        self.notifActivatedCheckBox.stateChanged.connect(self.notif_activated_checkbox_state_changed)

        grid.addWidget(self.notifActivatedCheckBox, 1, 1)

        lbl = QLabel("Toutes les...")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.timeTextEdit = QLineEdit()
        self.timeTextEdit.setFixedWidth(50)
        self.timeTextEdit.setFixedHeight(30)
        self.timeTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.timeTextEdit, 2, 1)

        self.timeUnitComboBox = QComboBox()
        self.timeUnitComboBox.setFixedWidth(100)
        self.timeUnitComboBox.setFixedHeight(30)
        self.timeUnitComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.timeUnitComboBox, 2, 2)

        time_units = ["minutes", "heures"]
        for i in range(0, len(time_units)):
            self.timeUnitComboBox.insertItem(i, str(time_units[i]))

        lbl = QLabel("GANTT")
        lbl.setFont(QFont('AnyStyle', self.titleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 3, 0, 1, 3)

        lbl = QLabel("Activé")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 4, 0)

        self.ganttActivatedCheckBox = QCheckBox()
        self.ganttActivatedCheckBox.stateChanged.connect(self.gantt_activated_checkbox_state_changed)

        grid.addWidget(self.ganttActivatedCheckBox, 4, 1)

        lbl = QLabel("Si pas de date de fin :")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 5, 0)

        self.NoEndDateComboBox = QComboBox()
        # self.NoEndDateComboBox.setFixedWidth(100)
        self.NoEndDateComboBox.setFixedHeight(30)
        self.NoEndDateComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.NoEndDateComboBox, 5, 1, 1, 2)

        no_end_date_choices = ["Appliquer une durée", "La fixer à aujourd'hui"]
        for i in range(0, len(no_end_date_choices)):
            self.NoEndDateComboBox.insertItem(i, str(no_end_date_choices[i]))

        lbl = QLabel("Durée (jours ouvrés)")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 6, 0)

        self.durationTextEdit = QLineEdit()
        self.durationTextEdit.setFixedWidth(50)
        self.durationTextEdit.setFixedHeight(30)
        self.durationTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.durationTextEdit, 6, 1)

        self.NoEndDateComboBox.currentTextChanged.connect(self.no_end_date_combobox_changed)

        enter_btn = QPushButton("Entrer")
        enter_btn.setFixedHeight(30)
        # enter_btn.setFixedWidth(90)
        enter_btn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        enter_btn.clicked.connect(self.enter_btn_clicked)
        grid.addWidget(enter_btn, 7, 0, 1, 3)

        self.setLayout(grid)
        enter_btn.setDefault(True)

    def showEvent(self, event):
        if self.mainWin.os == 'linux':
            self.move(
                QGuiApplication.screenAt(QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())

        self.modifying = True
        if self.mainWin.config["notif"]:
            self.notifActivatedCheckBox.setChecked(True)
            self.timeTextEdit.setEnabled(True)
            self.timeUnitComboBox.setEnabled(True)
        else:
            self.notifActivatedCheckBox.setChecked(False)
            self.timeTextEdit.setEnabled(False)
            self.timeUnitComboBox.setEnabled(False)
        self.timeTextEdit.setText(self.mainWin.config["period"])
        self.timeUnitComboBox.setCurrentText(self.mainWin.config["unit"])

        if self.mainWin.config["gantt"]:
            self.ganttActivatedCheckBox.setChecked(True)
            self.NoEndDateComboBox.setEnabled(True)
            self.durationTextEdit.setEnabled(True)
        else:
            self.ganttActivatedCheckBox.setChecked(False)
            self.NoEndDateComboBox.setEnabled(False)
            self.durationTextEdit.setEnabled(False)
        self.NoEndDateComboBox.setCurrentText(self.mainWin.config["no_end_date_format"])
        self.durationTextEdit.setText(self.mainWin.config["no_end_date"])

    def hideEvent(self, event):
        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de paramétrage")
            msg.setText("Les modifications ne seront pas prises en compte")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.on_hide_msg_box_btn_clicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            # msg.exec_()
            msg.exec()

    def on_hide_msg_box_btn_clicked(self, button):
        if button.text() == "OK":
            self.modifying = False
        elif button.text() == "Annuler":
            self.show()

    def notif_activated_checkbox_state_changed(self):
        if self.notifActivatedCheckBox.isChecked():
            self.timeTextEdit.setEnabled(True)
            self.timeUnitComboBox.setEnabled(True)
        else:
            self.timeTextEdit.setEnabled(False)
            self.timeUnitComboBox.setEnabled(False)

    def gantt_activated_checkbox_state_changed(self):
        if self.ganttActivatedCheckBox.isChecked():
            self.durationTextEdit.setEnabled(True)
            self.NoEndDateComboBox.setEnabled(True)
        else:
            self.durationTextEdit.setEnabled(False)
            self.NoEndDateComboBox.setEnabled(False)

    def no_end_date_combobox_changed(self, text):
        if text == "La fixer à aujourd'hui":
            self.durationTextEdit.setEnabled(False)
        else:
            self.durationTextEdit.setEnabled(True)

    def enter_btn_clicked(self):

        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de paramétrage")
            msg.setText("Les paramètres vont être modifiés")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.on_enter_msg_box_btn_clicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

        else:
            self.hide()

    def on_enter_msg_box_btn_clicked(self, button):
        if button.text() == "OK":
            self.mainWin.config["notif"] = self.notifActivatedCheckBox.isChecked()
            self.mainWin.config["period"] = self.timeTextEdit.text()
            self.mainWin.config["unit"] = self.timeUnitComboBox.currentText()
            self.mainWin.config["gantt"] = self.ganttActivatedCheckBox.isChecked()
            self.mainWin.config["no_end_date_format"] = self.NoEndDateComboBox.currentText()
            self.mainWin.config["no_end_date"] = self.durationTextEdit.text()
            self.modifying = False
            self.mainWin.modified_config.emit()
            self.hide()
