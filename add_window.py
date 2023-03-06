from PySide2.QtCore import Qt, QDateTime, QDate
from PySide2.QtGui import QFont, QTextOption
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDateEdit, \
    QDialog, QPlainTextEdit, QMessageBox, QComboBox


class AddTaskDialog(QDialog):

    def __init__(self, mainWin):
        super(AddTaskDialog, self).__init__()

        self.mainWin = mainWin

        self.modifying = False
        self.task = None

        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Ajouter une tâche")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 9.5

        grid = QGridLayout()

        lbl = QLabel("Nom")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0)

        self.nameTextEdit = QLineEdit()
        self.nameTextEdit.setFixedWidth(240)
        self.nameTextEdit.setFixedHeight(30)
        self.nameTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.nameTextEdit, 0, 1)

        lbl = QLabel("Description")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 1, 0)

        self.descTextEdit = QPlainTextEdit()
        self.descTextEdit.setFixedWidth(240)
        self.descTextEdit.setFixedHeight(110)
        self.descTextEdit.setWordWrapMode(QTextOption.WordWrap.WrapAtWordBoundaryOrAnywhere)
        self.descTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.descTextEdit, 1, 1)

        lbl = QLabel("Projet")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.projectComboBox = QComboBox()
        self.projectComboBox.setFixedWidth(240)
        self.projectComboBox.setFixedHeight(30)
        self.projectComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        self.projectComboBox.currentIndexChanged.connect(self.ProjectComboBoxIndexChanged)
        grid.addWidget(self.projectComboBox, 2, 1)

        lbl = QLabel("Date de début")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 3, 0)

        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setDateTime(QDateTime.currentDateTime())
        self.startDateEdit.setFixedWidth(210)
        self.startDateEdit.setFixedHeight(30)
        self.startDateEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.startDateEdit, 3, 1, Qt.AlignRight)

        lbl = QLabel("Date de fin")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 4, 0)

        endDateLayout = QHBoxLayout()

        self.endDateCheckBox = QCheckBox()
        self.endDateCheckBox.stateChanged.connect(self.EndDateCheckBoxStateChanged)

        self.endDateEdit = QDateEdit(calendarPopup=True)
        self.endDateEdit.setEnabled(False)
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())
        self.endDateEdit.setFixedWidth(210)
        self.endDateEdit.setFixedHeight(30)
        self.endDateEdit.setFont(QFont('AnyStyle', self.itemFontSize))

        endDateLayout.addWidget(self.endDateCheckBox, 0)
        endDateLayout.addWidget(self.endDateEdit, 1)

        grid.addLayout(endDateLayout, 4, 1)

        enterTaskBtn = QPushButton("Entrer")
        enterTaskBtn.setFixedHeight(30)
        # enterTaskBtn.setFixedWidth(90)
        enterTaskBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        enterTaskBtn.clicked.connect(self.EnterTaskBtnClicked)
        grid.addWidget(enterTaskBtn, 5, 0, 1, 2)

        self.setLayout(grid)

        # self.hide.connect(self.HideActions)

    """def HideActions(self):
        print("hide")"""

    def hideEvent(self, event):
        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de tâche")
            msg.setText("Les modifications ne seront pas prises en compte")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onHideMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

        else:
            self.nameTextEdit.setText("")
            self.descTextEdit.setPlainText("")
            self.startDateEdit.setDateTime(QDateTime.currentDateTime())
            self.endDateCheckBox.setChecked(False)
            self.endDateEdit.setDateTime(QDateTime.currentDateTime())
            self.setWindowTitle("Ajouter une tâche")

    def onHideMsgBoxBtnClicked(self, button):
        if button.text() == "OK":
            self.nameTextEdit.setText("")
            self.descTextEdit.setPlainText("")
            self.startDateEdit.setDateTime(QDateTime.currentDateTime())
            self.endDateCheckBox.setChecked(False)
            self.endDateEdit.setDateTime(QDateTime.currentDateTime())
            self.setWindowTitle("Ajouter une tâche")
            self.modifying = False
        elif button.text() == "Annuler":
            self.show()

    def EndDateCheckBoxStateChanged(self):
        if self.endDateCheckBox.isChecked():
            self.endDateEdit.setEnabled(True)
        else:
            self.endDateEdit.setEnabled(False)

    def EnterTaskBtnClicked(self):
        taskName = self.nameTextEdit.text()
        taskProject = self.projectComboBox.currentText()
        taskDescription = self.descTextEdit.toPlainText()
        taskStartDate = self.startDateEdit.date().toString(Qt.ISODate)
        if not self.endDateCheckBox.isChecked():
            taskEndDate = "-"
        else:
            taskEndDate = self.endDateEdit.date().toString(Qt.ISODate)
        self.task = {"Check": 0, "Name": taskName, "Description": taskDescription, "Project": taskProject, "StartDate": taskStartDate, "EndDate": taskEndDate}


        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de tâche")
            msg.setText("La tâche va être modifiée")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onEnterMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

        else:
            self.mainWin.new_task.emit(self.task)
            self.hide()

    def onEnterMsgBoxBtnClicked(self, button):
        if button.text() == "OK":
            self.mainWin.modified_task.emit(self.task)
            self.modifying = False
            self.hide()

    def ModifyTask(self, task):
        self.nameTextEdit.setText(task["Name"])
        self.descTextEdit.setPlainText(task["Description"])
        self.projectComboBox.setCurrentText(task["Project"])
        self.startDateEdit.setDate(QDate.fromString(task["StartDate"], Qt.ISODate))
        if task["EndDate"] == "-":
            self.endDateEdit.setDate(QDate.currentDate())
            self.endDateCheckBox.setChecked(False)
        else:
            self.endDateEdit.setDate(QDate.fromString(task["EndDate"], Qt.ISODate))
            self.endDateCheckBox.setChecked(True)

        self.setWindowTitle("Modifier une tâche")

        self.modifying = True

        self.show()

    def ProjectComboBoxIndexChanged(self, index):
        if index == len(self.mainWin.projectList):
            self.mainWin.get_new_project.emit()