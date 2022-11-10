import os
import sys
import math
import shutil
import time

from pathlib import Path

import yaml
from PySide2.QtCore import Qt, Signal, QSize, QDateTime, QDate
from PySide2.QtGui import QFont, QPalette, QColor, QTextOption
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QWidget, QListWidget, QApplication, \
    QLabel, QPushButton, QCheckBox, QTreeWidget, QTreeWidgetItem, QHeaderView, QDateEdit, QDialog, QVBoxLayout, \
    QPlainTextEdit, QMessageBox, QInputDialog


class AddTaskDialog(QDialog):

    def __init__(self, mainWin):
        super(AddTaskDialog, self).__init__()

        self.mainWin = mainWin

        self.modifying = False
        self.task = None

        self.setWindowTitle("Ajouter une tâche")

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        lbl = QLabel("Nom")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0)

        self.nameTextEdit = QLineEdit()
        self.nameTextEdit.setFixedWidth(200)
        self.nameTextEdit.setFixedHeight(30)
        self.nameTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.nameTextEdit, 0, 1)

        lbl = QLabel("Description")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 1, 0)

        self.descTextEdit = QPlainTextEdit()
        self.descTextEdit.setFixedWidth(200)
        self.descTextEdit.setFixedHeight(90)
        self.descTextEdit.setWordWrapMode(QTextOption.WordWrap.WrapAtWordBoundaryOrAnywhere)
        self.descTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.descTextEdit, 1, 1)

        lbl = QLabel("Date de début")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setDateTime(QDateTime.currentDateTime())
        self.startDateEdit.setFixedWidth(170)
        self.startDateEdit.setFixedHeight(30)
        self.startDateEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.startDateEdit, 2, 1, Qt.AlignRight)

        lbl = QLabel("Date de fin")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 3, 0)

        endDateLayout = QHBoxLayout()

        self.endDateCheckBox = QCheckBox()
        self.endDateCheckBox.stateChanged.connect(self.EndDateCheckBoxStateChanged)
        endDateLayout.addWidget(self.endDateCheckBox, 0)

        self.endDateEdit = QDateEdit(calendarPopup=True)
        self.endDateEdit.setEnabled(False)
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())
        self.endDateEdit.setFixedWidth(170)
        self.endDateEdit.setFixedHeight(30)
        self.endDateEdit.setFont(QFont('AnyStyle', itemFontSize))
        endDateLayout.addWidget(self.endDateEdit, 1)

        grid.addLayout(endDateLayout, 3, 1)

        enterTaskBtn = QPushButton("Entrer")
        enterTaskBtn.setFixedHeight(30)
        # enterTaskBtn.setFixedWidth(90)
        enterTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        enterTaskBtn.clicked.connect(self.EnterTaskBtnClicked)
        grid.addWidget(enterTaskBtn, 4, 0, 1, 2)

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
        # taskDescription = self.descTextEdit.text()
        taskDescription = self.descTextEdit.toPlainText()
        taskStartDate = self.startDateEdit.date().toString(Qt.ISODate)
        if not self.endDateCheckBox.isChecked():
            taskEndDate = "-"
        else:
            taskEndDate = self.endDateEdit.date().toString(Qt.ISODate)
        self.task = {"Check": 0,"Name": taskName, "Description": taskDescription, "StartDate": taskStartDate, "EndDate": taskEndDate}


        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de tâche")
            msg.setText("La tâche va être modifiée")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onEnterMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
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
        self.nameTextEdit.setText(task[0])
        self.descTextEdit.setPlainText(task[1])
        self.startDateEdit.setDate(QDate.fromString(task[2], Qt.ISODate))
        if task[3] == "-":
            self.endDateEdit.setDate(QDate.currentDate())
            self.endDateCheckBox.setChecked(False)
        else:
            self.endDateEdit.setDate(QDate.fromString(task[3], Qt.ISODate))
            self.endDateCheckBox.setChecked(True)

        self.setWindowTitle("Modifier une tâche")

        self.modifying = True

        self.show()


class ProjectsDialog(QDialog):

    def __init__(self, mainWin):
        super(ProjectsDialog, self).__init__()

        self.mainWin = mainWin

        self.setWindowTitle("Gestion des projets")

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        buttonLayout = QVBoxLayout()

        AddProjectBtn = QPushButton("Ajouter")
        AddProjectBtn.setFixedHeight(30)
        AddProjectBtn.setFixedWidth(100)
        AddProjectBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        AddProjectBtn.clicked.connect(self.AddProjectBtnClicked)
        buttonLayout.addWidget(AddProjectBtn, 0)

        DelProjectBtn = QPushButton("Supprimer")
        DelProjectBtn.setFixedHeight(30)
        DelProjectBtn.setFixedWidth(100)
        DelProjectBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        DelProjectBtn.clicked.connect(self.DeleteProjectBtnClicked)
        buttonLayout.addWidget(DelProjectBtn, 1)

        grid.addLayout(buttonLayout, 0, 0)

        self.projectTree = QTreeWidget()
        self.projectTree.setHeaderHidden(True)
        self.projectTree.setFont(QFont('AnyStyle', itemFontSize))
        self.projectTree.setFixedWidth(300)
        self.projectTree.setFixedHeight(300)
        self.projectTree.itemChanged.connect(self.projectTree_changed)
        self.projectTree.itemClicked.connect(self.projectTree_itemClicked)
        self.projectTree.itemDoubleClicked.connect(self.ModifyProjectBtnClicked)
        grid.addWidget(self.projectTree, 0, 1)

        self.Update_project_tree()

        self.setLayout(grid)

    def Save(self):
        with open('projects.yaml', 'w') as f:
            yaml.dump(self.mainWin.projectList, f, sort_keys=False)

    def Update_project_tree(self):
        self.projectTree.clear()
        for project in self.mainWin.projectList:
            elmt = QTreeWidgetItem(self.projectTree)
            elmt.setText(0, project["Name"])

    def AddProjectBtnClicked(self):
        text, ok = QInputDialog.getText(self, 'Entrer un projet', 'Nom du projet :')
        if ok:
            self.mainWin.projectList.append({"Name": text})

        self.Save()
        self.Update_project_tree()

    def DeleteProjectBtnClicked(self):
        pass

    def projectTree_changed(self):
        pass

    def projectTree_itemClicked(self):
        pass

    def ModifyProjectBtnClicked(self):
        pass


class MainWindow(QWidget):

    new_task = Signal(object)
    modify_task = Signal(object)
    modified_task = Signal(object)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.os = sys.platform
        path1 = os.fspath(Path(__file__).resolve().parent / "main.py")
        path2 = os.fspath(Path(__file__).resolve().parent / "main.pyw")
        shutil.copyfile(path1, path2)

        # linux shortcut
        if self.os == 'linux':
            path = os.fspath(Path(__file__).resolve().parent / "TaskManager.desktop")
            if not os.path.exists(path):
                f = open(path, 'w')
                f.write('[Desktop Entry]\n')
                f.write('Name = Task Manager\n')
                d = os.getcwd()
                f.write(f'Exec=/usr/bin/python3 {d}/main.py\n')
                f.write('Terminal=false\n')
                f.write('Type=Application\n')
                f.close()

        self.setWindowTitle("Task Manager")
        self.setFixedWidth(1000)
        self.setFixedHeight(500)

        self.tasksList = []
        self.projectList = []
        self.selectedItem = None
        self.updating = False

        try:
            with open('tasks.yaml', 'r') as f:
                self.tasksList = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open('tasks.yaml', 'w') as f:
                yaml.dump(None, f, sort_keys=False)

        try:
            with open('projects.yaml', 'r') as f:
                self.projectList = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open('projects.yaml', 'w') as f:
                yaml.dump(None, f, sort_keys=False)

        self.addTaskDialog = AddTaskDialog(self)
        self.projectsDialog = ProjectsDialog(self)

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        self.listTree = QTreeWidget()
        self.listTree.setHeaderLabels(["", "Nom", "Description", "Début", "Fin"])
        self.listTree.setFont(QFont('AnyStyle', subtitleFontSize))
        self.listTree.setColumnWidth(0, 50)
        self.listTree.setColumnWidth(1, 200)
        self.listTree.setColumnWidth(2, 480)
        self.listTree.setColumnWidth(3, 120)
        self.listTree.setColumnWidth(4, 120)
        self.listTree.itemChanged.connect(self.listTree_changed)
        self.listTree.itemClicked.connect(self.listTree_itemClicked)
        self.listTree.itemDoubleClicked.connect(self.ModifyTaskBtnClicked)
        grid.addWidget(self.listTree, 2, 0, 1, 4)

        self.listTreeHeader = self.listTree.header()
        self.listTreeHeader.setSectionResizeMode(QHeaderView.Fixed)
        self.listTreeHeader.setStretchLastSection(False)
        # self.listTreeHeader.setSectionResizeMode()

        addDeleteLayout = QHBoxLayout()

        addTaskBtn = QPushButton("Ajouter")
        addTaskBtn.setFixedHeight(30)
        addTaskBtn.setFixedWidth(150)
        addTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        addTaskBtn.clicked.connect(self.AddTaskBtnClicked)
        addDeleteLayout.addWidget(addTaskBtn, 0)

        manageProjectsBtn = QPushButton("Gestion projets")
        manageProjectsBtn.setFixedHeight(30)
        manageProjectsBtn.setFixedWidth(150)
        manageProjectsBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        manageProjectsBtn.clicked.connect(self.ManageProjectsBtnClicked)
        addDeleteLayout.addWidget(manageProjectsBtn, 1)

        delTaskBtn = QPushButton("Supprimer")
        delTaskBtn.setFixedHeight(30)
        delTaskBtn.setFixedWidth(150)
        delTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        delTaskBtn.clicked.connect(self.DeleteTaskBtnClicked)
        addDeleteLayout.addWidget(delTaskBtn, 2)

        grid.addLayout(addDeleteLayout, 3, 0, 1, 4)

        self.setLayout(grid)

        self.Update_changes()

        self.new_task.connect(self.New_task)
        self.modify_task.connect(self.addTaskDialog.ModifyTask)
        self.modified_task.connect(self.ModifiedTask)

    def Save(self):
        with open('tasks.yaml', 'w') as f:
            yaml.dump(self.tasksList, f, sort_keys=False)

    def New_task(self, task):
        self.tasksList.append(task)

        self.Save()
        self.Update_changes()

    def Update_changes(self):

        self.listTree.clear()
        for task in self.tasksList:
            self.updating = True
            elmt = QTreeWidgetItem(self.listTree)
            elmt.setFlags(elmt.flags() | Qt.ItemIsUserCheckable)

            lbl = QLabel(task["Name"])
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.listTree.setItemWidget(elmt, 1, lbl)

            lbl = QLabel(task["Description"])
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.listTree.setItemWidget(elmt, 2, lbl)

            lbl = QLabel(task["StartDate"])
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.listTree.setItemWidget(elmt, 3, lbl)

            lbl = QLabel(task["EndDate"])
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.listTree.setItemWidget(elmt, 4, lbl)

            self.updating = False

            if task["Check"] == 1:
                elmt.setCheckState(0, Qt.Checked)
            else:
                elmt.setCheckState(0, Qt.Unchecked)



    def listTree_changed(self, item, col):
        if not self.updating:
            if item.checkState(0) == Qt.Checked:
                for task in self.tasksList:
                    if task["Name"] == self.listTree.itemWidget(item, 1).text() and task["Description"] == self.listTree.itemWidget(item, 2).text():
                        task["Check"] = 1
                        break
                for i in range(1, self.listTree.columnCount()):
                    itemWidget = self.listTree.itemWidget(item, i)
                    f = itemWidget.font()
                    f.setStrikeOut(True)
                    itemWidget.setFont(f)

            elif item.checkState(0) == Qt.Unchecked:
                for task in self.tasksList:
                    if task["Name"] == self.listTree.itemWidget(item, 1).text() and task["Description"] == self.listTree.itemWidget(item, 2).text():
                        task["Check"] = 0
                        break
                for i in range(1, self.listTree.columnCount()):
                    itemWidget = self.listTree.itemWidget(item, i)
                    f = itemWidget.font()
                    f.setStrikeOut(False)
                    itemWidget.setFont(f)

            self.Save()

    def listTree_itemClicked(self, item, col):
        if item.isSelected():
            self.selectedItem = item

    def AddTaskBtnClicked(self):
        self.addTaskDialog.show()

    def ModifyTaskBtnClicked(self):

        taskToSend = []
        for i in range(1, self.listTree.columnCount()):
            taskToSend.append(self.listTree.itemWidget(self.selectedItem, i).text())

        self.modify_task.emit(taskToSend)

    def ModifiedTask(self, modifiedTask):
        for task in self.tasksList:
            if task["Name"] == self.listTree.itemWidget(self.selectedItem, 1).text() and task["Description"] ==self.listTree.itemWidget(self.selectedItem, 2).text():
                task["Name"] = modifiedTask["Name"]
                task["Description"] = modifiedTask["Description"]
                task["StartDate"] = modifiedTask["StartDate"]
                task["EndDate"] = modifiedTask["EndDate"]
                break

        self.Save()
        self.Update_changes()

    def DeleteTaskBtnClicked(self):

        taskToDelete = None
        for task in self.tasksList:
            if task["Name"] == self.listTree.itemWidget(self.selectedItem, 1).text() and task["Description"] == self.listTree.itemWidget(self.selectedItem, 2).text():
                taskToDelete = task
                break

        self.tasksList.remove(taskToDelete)

        # task = {"Name": taskName, "Description": taskDescription, "StartDate": taskStart, "EndDate": taskEnd}
        # self.tasksList.remove(task)

        self.Save()
        self.Update_changes()

    def ManageProjectsBtnClicked(self):
        self.projectsDialog.show()

if __name__ == "__main__":
    app = QApplication([])

    app.setStyle("Fusion")

    # Palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Window, palette.window().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.WindowText, palette.windowText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Base, palette.base().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.AlternateBase, palette.alternateBase().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ToolTipBase, palette.toolTipBase().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ToolTipText, palette.toolTipText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Text, palette.text().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Button, palette.button().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, palette.buttonText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.BrightText, palette.brightText().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Link, palette.link().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.Highlight, palette.highlight().color().lighter())
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, palette.highlightedText().color().lighter())
    app.setPalette(palette)

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
