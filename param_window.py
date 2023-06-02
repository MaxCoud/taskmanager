from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QGuiApplication, QCursor
from PySide2.QtWidgets import QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDialog, QMessageBox, QComboBox


class ParamDialog(QDialog):

    def __init__(self, mainWin):
        super(ParamDialog, self).__init__()

        self.mainWin = mainWin

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
        self.notifActivatedCheckBox.stateChanged.connect(self.NotifActivatedCheckBoxStateChanged)

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

        timeUnits = ["minutes", "heures"]
        for i in range(0, len(timeUnits)):
            self.timeUnitComboBox.insertItem(i, str(timeUnits[i]))

        enterBtn = QPushButton("Entrer")
        enterBtn.setFixedHeight(30)
        # enterBtn.setFixedWidth(90)
        enterBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        enterBtn.clicked.connect(self.EnterBtnClicked)
        grid.addWidget(enterBtn, 3, 0, 1, 3)

        self.setLayout(grid)
        enterBtn.setDefault(True)

    def showEvent(self, event):
        self.move(QGuiApplication.screenAt(QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())
        self.modifying = True
        if self.mainWin.config["notif"]:
            self.notifActivatedCheckBox.setChecked(True)
        else:
            self.notifActivatedCheckBox.setChecked(False)
        self.timeTextEdit.setText(self.mainWin.config["period"])
        self.timeUnitComboBox.setCurrentText(self.mainWin.config["unit"])

    def hideEvent(self, event):
        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de paramétrage")
            msg.setText("Les modifications ne seront pas prises en compte")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onHideMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

    def onHideMsgBoxBtnClicked(self, button):
        if button.text() == "OK":
            self.modifying = False
        elif button.text() == "Annuler":
            self.show()

    def NotifActivatedCheckBoxStateChanged(self):
        if self.notifActivatedCheckBox.isChecked():
            self.timeTextEdit.setEnabled(True)
            self.timeUnitComboBox.setEnabled(True)
        else:
            self.timeTextEdit.setEnabled(False)
            self.timeUnitComboBox.setEnabled(False)

    def EnterBtnClicked(self):

        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de paramétrage")
            msg.setText("Les paramètres vont être modifiés")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onEnterMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

        else:
            self.hide()

    def onEnterMsgBoxBtnClicked(self, button):
        if button.text() == "OK":
            self.mainWin.config["notif"] = self.notifActivatedCheckBox.isChecked()
            self.mainWin.config["period"] = self.timeTextEdit.text()
            self.mainWin.config["unit"] = self.timeUnitComboBox.currentText()
            self.modifying = False
            self.mainWin.modified_config.emit()
            self.hide()
