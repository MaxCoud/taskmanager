import os
import sys
import math
import shutil
import time

from pathlib import Path

import yaml
from PySide2.QtCore import Qt, Signal, QSize
from PySide2.QtGui import QFont, QPalette, QColor, QPen, QPainter
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QWidget, QListWidget, QApplication, \
    QLabel, QPushButton, QCheckBox, QTreeWidget, QTreeWidgetItem, QHeaderView


class MainWindow(QWidget):

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

        self.tasksList = []

        try:
            with open('tasks.yaml', 'r') as f:
                self.tasksList = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open('tasks.yaml', 'w') as f:
                yaml.dump(None, f, sort_keys=False)

        titleFontSize = 14
        subtitleFontSize = 11
        itemFontSize = 9

        grid = QGridLayout()

        lbl = QLabel("Nom")
        lbl.setFont(QFont('AnyStyle', titleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0)

        lbl = QLabel("Description")
        lbl.setFont(QFont('AnyStyle', titleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 1)

        self.nameTextEdit = QLineEdit()
        self.nameTextEdit.setFixedWidth(200)
        self.nameTextEdit.setFixedHeight(30)
        self.nameTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.nameTextEdit, 1, 0)

        self.descTextEdit = QLineEdit()
        self.descTextEdit.setFixedWidth(600)
        self.descTextEdit.setFixedHeight(30)
        self.descTextEdit.setFont(QFont('AnyStyle', itemFontSize))
        grid.addWidget(self.descTextEdit, 1, 1)

        enterTaskBtn = QPushButton("Entrer")
        enterTaskBtn.setFixedHeight(30)
        enterTaskBtn.setFixedWidth(90)
        enterTaskBtn.setFont(QFont('AnyStyle', subtitleFontSize))
        enterTaskBtn.clicked.connect(self.EnterTaskBtnClicked)
        grid.addWidget(enterTaskBtn, 1, 2)

        self.listTree = QTreeWidget()
        self.listTree.setHeaderLabels(["", "Nom", "Description"])
        self.listTree.setFont(QFont('AnyStyle', subtitleFontSize))
        self.listTree.itemChanged.connect(self.listTree_changed)
        grid.addWidget(self.listTree, 2, 0, 1, 3)

        self.listTreeHeader = self.listTree.header()
        self.listTreeHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.listTreeHeader.setStretchLastSection(False)
        # self.listTreeHeader.setSectionResizeMode()

        self.setLayout(grid)

        self.Update_changes()

    def Save(self):
        with open('tasks.yaml', 'w') as f:
            yaml.dump(self.tasksList, f, sort_keys=False)

    def EnterTaskBtnClicked(self):
        taskName = self.nameTextEdit.text()
        taskDescription = self.descTextEdit.text()
        task = {"Name": taskName, "Description": taskDescription}
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
            elmt.setTextAlignment(1, Qt.AlignCenter)
            elmt.setTextAlignment(2, Qt.AlignLeft)
            # toolTip = "test"
            # elmt.setToolTip(0, toolTip)
            elmt.setCheckState(0, Qt.Unchecked)

    def listTree_changed(self, item, col):
        if item.checkState(0) == Qt.Checked:
            f1 = item.font(1)
            f1.setStrikeOut(True)
            item.setFont(1, f1)
            f2 = item.font(2)
            f2.setStrikeOut(True)
            item.setFont(2, f2)
        elif item.checkState(0) == Qt.Unchecked:
            f1 = item.font(1)
            f1.setStrikeOut(False)
            item.setFont(1, f1)
            f2 = item.font(2)
            f2.setStrikeOut(False)
            item.setFont(2, f2)

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
