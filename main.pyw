import os
import sys
import math
import shutil
import time

from pathlib import Path

import yaml
from PySide2.QtCore import Qt, Signal, QSize, QDateTime, QDate
from PySide2.QtGui import QFont, QPalette, QColor, QPen, QPainter
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QWidget, QListWidget, QApplication, \
    QLabel, QPushButton, QCheckBox, QTreeWidget, QTreeWidgetItem, QHeaderView, QDateEdit, QDialog, QVBoxLayout


class AddTaskDialog(QDialog):

    def __init__(self, mainWin):
        super(AddTaskDialog, self).__init__()

        self.mainWin = mainWin

        self.setWindowTitle("Ajouter une tâche")

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        lbl = QLabel("Nom")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0)

        lbl = QLabel("Description")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 1, 0)

        lbl = QLabel("Date de fin")
        lbl.setFont(QFont('AnyStyle', subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.nameTextEdit = QLineEdit()
        self.nameTextEdit.setFixedWidth(200)
        self.nameTextEdit.setFixedHeight(30)
        self.nameTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.nameTextEdit, 0, 1)

        self.descTextEdit = QLineEdit()
        self.descTextEdit.setFixedWidth(200)
        self.descTextEdit.setFixedHeight(90)
        self.descTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.descTextEdit, 1, 1)

        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setEnabled(False)
        self.startDateEdit.setDateTime(QDateTime.currentDateTime())
        self.startDateEdit.setFixedWidth(200)
        self.startDateEdit.setFixedHeight(30)
        self.startDateEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.startDateEdit, 2, 1)

        endDateLayout = QHBoxLayout()

        self.endDateCheckBox = QCheckBox()
        self.endDateCheckBox.stateChanged.connect(self.EndDateCheckBoxStateChanged)
        endDateLayout.addWidget(self.endDateCheckBox, 0)

        self.endDateEdit = QDateEdit(calendarPopup=True)
        self.endDateEdit.setEnabled(False)
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())
        self.endDateEdit.setFixedWidth(180)
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

    def EndDateCheckBoxStateChanged(self):
        if self.endDateCheckBox.isChecked():
            self.endDateEdit.setEnabled(True)
        else:
            self.endDateEdit.setEnabled(False)

    def EnterTaskBtnClicked(self):
        taskName = self.nameTextEdit.text()
        taskDescription = self.descTextEdit.text()
        taskStartDate = QDate.currentDate().toString(Qt.ISODate)
        if not self.endDateCheckBox.isChecked():
            taskEndDate = "-"
        else:
            taskEndDate = self.endDateEdit.date().toString(Qt.ISODate)
        task = {"Name": taskName, "Description": taskDescription, "StartDate": taskStartDate, "EndDate": taskEndDate}
        self.mainWin.new_task.emit(task)

        self.hide()



class MainWindow(QWidget):

    new_task = Signal(object)

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
        self.selectedItem = None

        try:
            with open('tasks.yaml', 'r') as f:
                self.tasksList = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open('tasks.yaml', 'w') as f:
                yaml.dump(None, f, sort_keys=False)

        self.addTaskDialog = AddTaskDialog(self)

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        self.listTree = QTreeWidget()
        self.listTree.setHeaderLabels(["", "Nom", "Description", "Début", "Fin"])
        self.listTree.setFont(QFont('AnyStyle', subtitleFontSize))
        self.listTree.itemChanged.connect(self.listTree_changed)
        self.listTree.itemClicked.connect(self.listTree_itemClicked)
        grid.addWidget(self.listTree, 2, 0, 1, 4)

        self.listTreeHeader = self.listTree.header()
        self.listTreeHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.listTreeHeader.setStretchLastSection(False)
        # self.listTreeHeader.setSectionResizeMode()

        modifyDeleteLayout = QHBoxLayout()

        addTaskBtn = QPushButton("Ajouter")
        addTaskBtn.setFixedHeight(30)
        addTaskBtn.setFixedWidth(100)
        addTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        addTaskBtn.clicked.connect(self.AddTaskBtnClicked)
        modifyDeleteLayout.addWidget(addTaskBtn, 0)

        modifyTaskBtn = QPushButton("Modifier")
        modifyTaskBtn.setFixedHeight(30)
        modifyTaskBtn.setFixedWidth(100)
        modifyTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        modifyTaskBtn.clicked.connect(self.ModifyTaskBtnClicked)
        modifyDeleteLayout.addWidget(modifyTaskBtn, 0)

        delTaskBtn = QPushButton("Supprimer")
        delTaskBtn.setFixedHeight(30)
        delTaskBtn.setFixedWidth(100)
        delTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        delTaskBtn.clicked.connect(self.DeleteTaskBtnClicked)
        modifyDeleteLayout.addWidget(delTaskBtn, 1)

        grid.addLayout(modifyDeleteLayout, 3, 0, 1, 4)

        self.setLayout(grid)

        self.Update_changes()

        self.new_task.connect(self.New_task)

    def Save(self):
        with open('tasks.yaml', 'w') as f:
            yaml.dump(self.tasksList, f, sort_keys=False)

    def EndDateCheckBoxStateChanged(self):
        if self.endDateCheckBox.isChecked():
            self.endDateEdit.setEnabled(True)
        else:
            self.endDateEdit.setEnabled(False)

    def EnterTaskBtnClicked(self):
        taskName = self.nameTextEdit.text()
        taskDescription = self.descTextEdit.text()
        taskStartDate = QDate.currentDate().toString(Qt.ISODate)
        if self.endDateCheckBox.isChecked():
            taskEndDate = "-"
        else:
            taskEndDate = self.endDateEdit.date().toString(Qt.ISODate)
        task = {"Name": taskName, "Description": taskDescription, "StartDate": taskStartDate, "EndDate": taskEndDate}
        self.tasksList.append(task)

        self.Save()
        self.Update_changes()

    def New_task(self, task):
        self.tasksList.append(task)

        self.Save()
        self.Update_changes()

    def Update_changes(self):
        self.listTree.clear()
        for task in self.tasksList:
            elmt = QTreeWidgetItem(self.listTree)
            elmt.setFlags(elmt.flags() | Qt.ItemIsUserCheckable)

            elmt.setText(1, task["Name"])
            elmt.setText(2, task["Description"])
            elmt.setText(3, task["StartDate"])
            elmt.setText(4, task["EndDate"])
            elmt.setTextAlignment(1, Qt.AlignCenter)
            elmt.setTextAlignment(2, Qt.AlignLeft)
            elmt.setTextAlignment(3, Qt.AlignCenter)
            elmt.setTextAlignment(4, Qt.AlignCenter)
            # toolTip = "test"
            # elmt.setToolTip(0, toolTip)
            elmt.setCheckState(0, Qt.Unchecked)

    def listTree_changed(self, item, col):
        if item.checkState(0) == Qt.Checked:
            for i in range(1, self.listTree.columnCount()):
                f = item.font(i)
                f.setStrikeOut(True)
                item.setFont(i, f)

        elif item.checkState(0) == Qt.Unchecked:
            for i in range(1, self.listTree.columnCount()):
                f = item.font(i)
                f.setStrikeOut(False)
                item.setFont(i, f)

    def listTree_itemClicked(self, item, col):
        if item.isSelected():
            self.selectedItem = item

    def AddTaskBtnClicked(self):
        self.addTaskDialog.show()

    def ModifyTaskBtnClicked(self):
        pass

    def DeleteTaskBtnClicked(self):
        taskName = self.selectedItem.text(1)
        taskDescription = self.selectedItem.text(2)
        task = {"Name": taskName, "Description": taskDescription}
        self.tasksList.remove(task)

        self.Save()
        self.Update_changes()

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
