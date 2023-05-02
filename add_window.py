import os

from PySide2.QtCore import Qt, QDateTime, QDate
from PySide2.QtGui import QFont, QTextOption
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDateEdit, \
    QDialog, QPlainTextEdit, QMessageBox, QComboBox, QFileDialog, QAction, QMenu

from style import select_icon

class AddTaskDialog(QDialog):

    def __init__(self, mainWin):
        super(AddTaskDialog, self).__init__()

        self.mainWin = mainWin

        self.modifying = False
        self.task = None
        self.documentsList = []

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

        # lbl = QLabel("Projet")
        # lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        # lbl.setAlignment(Qt.AlignCenter)
        # grid.addWidget(lbl, 2, 0)
        #
        # self.projectComboBox = QComboBox()
        # self.projectComboBox.setFixedWidth(240)
        # self.projectComboBox.setFixedHeight(30)
        # self.projectComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        # self.projectComboBox.currentIndexChanged.connect(self.ProjectComboBoxIndexChanged)
        # grid.addWidget(self.projectComboBox, 2, 1)

        lbl = QLabel("Priorité")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.priorityComboBox = QComboBox()
        self.priorityComboBox.setFixedWidth(240)
        self.priorityComboBox.setFixedHeight(30)
        self.priorityComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.priorityComboBox, 2, 1)

        priorityDegrees = ["Normal", "Pressant", "Urgent"]
        for i in range(0, len(priorityDegrees)):
            self.priorityComboBox.insertItem(i, str(priorityDegrees[i]))

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

        lbl = QLabel("Documents")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 5, 0)

        browseLayout = QHBoxLayout()

        browseBtn = QPushButton("Parcourir")
        browseBtn.setFixedHeight(30)
        # browseBtn.setFixedWidth(90)
        browseBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        browseBtn.clicked.connect(self.BrowseBtnClicked)
        browseLayout.addWidget(browseBtn, 0)

        self.filesLayout = QGridLayout()
        self.filesLayoutRow = 0
        self.filesLayoutColumn = 0
        self.filesLabels = []

        # self.browseLbl = QLabel("oui")
        # self.browseLbl.setFont(QFont('AnyStyle', self.itemFontSize))
        # self.browseLbl.setAlignment(Qt.AlignLeft)
        # self.filesLayout.addWidget(self.browseLbl, 0, 0)

        browseLayout.addLayout(self.filesLayout)

        grid.addLayout(browseLayout, 5, 1)

        enterTaskBtn = QPushButton("Entrer")
        enterTaskBtn.setFixedHeight(30)
        # enterTaskBtn.setFixedWidth(90)
        enterTaskBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        enterTaskBtn.clicked.connect(self.EnterTaskBtnClicked)
        grid.addWidget(enterTaskBtn, 6, 0, 1, 2)

        self.setLayout(grid)
        enterTaskBtn.setDefault(True)

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

        for lbl in self.filesLabels:
            lbl.setParent(None)

        self.filesLabels = []
        self.filesLayoutColumn = 0
        self.filesLayoutRow = 0
        self.documentsList = []

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
        # taskProject = self.projectComboBox.currentText()
        taskPriority = self.priorityComboBox.currentText()
        taskDescription = self.descTextEdit.toPlainText()
        taskStartDate = self.startDateEdit.date().toString(Qt.ISODate)
        if not self.endDateCheckBox.isChecked():
            taskEndDate = "-"
        else:
            taskEndDate = self.endDateEdit.date().toString(Qt.ISODate)
        # self.task = {"Check": 0, "Name": taskName, "Description": taskDescription, "Project": taskProject, "StartDate": taskStartDate, "EndDate": taskEndDate}
        # self.task = {"Name": taskName, "Description": taskDescription, "Priority": taskPriority, "StartDate": taskStartDate, "EndDate": taskEndDate, "Check": 0}
        self.task = {"Name": taskName, "Description": taskDescription, "Priority": taskPriority,
                     "StartDate": taskStartDate, "EndDate": taskEndDate, "Check": 0,
                     "Documents": self.documentsList}


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
        # self.projectComboBox.setCurrentText(task["Project"])
        self.priorityComboBox.setCurrentText(task["Priority"])
        self.startDateEdit.setDate(QDate.fromString(task["StartDate"], Qt.ISODate))
        if task["EndDate"] == "-":
            self.endDateEdit.setDate(QDate.currentDate())
            self.endDateCheckBox.setChecked(False)
        else:
            self.endDateEdit.setDate(QDate.fromString(task["EndDate"], Qt.ISODate))
            self.endDateCheckBox.setChecked(True)

        if not "Documents" in task:
            task["Documents"] = []

        filesPaths = task["Documents"]

        # line_nb = len(filesPaths) // 6
        # row_nb = len(filesPaths) % 6
        # print("line_nb", line_nb)
        # print("row_nb", row_nb)

        self.display_selected_documents(filesPaths)

        self.setWindowTitle("Modifier une tâche")

        self.modifying = True

        self.show()

    def ProjectComboBoxIndexChanged(self, index):
        if index == len(self.mainWin.projectList):
            self.mainWin.get_new_project.emit()

    def BrowseBtnClicked(self):
        file = QFileDialog.getOpenFileNames(parent=self, caption="Sélectionner un fichier")
        filesPaths = file[0]

        self.display_selected_documents(filesPaths)

        # get a folder :
        # folder = QFileDialog.getExistingDirectory(parent=self, caption="Sélectionner un dossier")

    def display_selected_documents(self, filesPaths):
        if len(filesPaths) > 0:

            for document in filesPaths:

                splited_document_path = document.split(".")
                extension = splited_document_path[len(splited_document_path) - 1]

                icon = select_icon(self.mainWin.d, self.mainWin.slash, extension)

                path = f"<a href={document}><img src={icon}></a>"

                lbl = QLabel(path)
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                lbl.setToolTip(document)
                self.filesLabels.append(lbl)

                context_menu_fn = self.make_context_menu_fn(lbl)  # create a separate context menu for each label

                lbl.setContextMenuPolicy(Qt.CustomContextMenu)
                lbl.customContextMenuRequested.connect(context_menu_fn)

                if self.filesLayoutColumn < 6:
                    self.filesLayout.addWidget(lbl, self.filesLayoutRow, self.filesLayoutColumn)
                else:
                    self.filesLayoutRow += 1
                    self.filesLayoutColumn = 0
                    self.filesLayout.addWidget(lbl, self.filesLayoutRow, self.filesLayoutColumn)

                self.filesLayoutColumn += 1

                self.documentsList.append(document)

    def create_document_context_menu(self, lbl):  # Define a function to create the context menu for a QLabel

        context_menu = QMenu()
        delete_selection = QAction("Enlever de la sélection", context_menu)
        context_menu.addAction(delete_selection)

        def remove_label():  # remove the label from its parent
            lbl.setParent(None)
            self.filesLabels.remove(lbl)
            self.documentsList.remove(lbl.toolTip())

        delete_selection.triggered.connect(remove_label)
        return context_menu

    def make_context_menu_fn(self, lbl):  # Define a function to create a closure for a label
        context_menu = self.create_document_context_menu(lbl)

        def show_context_menu(pos):
            context_menu.exec_(lbl.mapToGlobal(pos))

        return show_context_menu
