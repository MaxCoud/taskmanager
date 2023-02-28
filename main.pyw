import os
import sys
import shutil
import time
from style import style

from pathlib import Path

import yaml
from PySide2.QtCore import Qt, Signal, QSize, QDateTime, QDate, QTimer
from PySide2.QtGui import QFont, QPalette, QColor, QTextOption, QKeySequence
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QWidget, QApplication, QLabel, QPushButton, \
    QCheckBox, QTreeWidget, QTreeWidgetItem, QHeaderView, QDateEdit, QDialog, QVBoxLayout, QPlainTextEdit, \
    QMessageBox, QInputDialog, QComboBox, QDesktopWidget, QTabWidget, QAction, QMainWindow, QMenu


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


class ProjectsDialog(QDialog):

    def __init__(self, mainWin):
        super(ProjectsDialog, self).__init__()

        self.mainWin = mainWin

        self.setWindowTitle("Gestion des projets")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.setWindowModality(Qt.ApplicationModal)

        self.selectedProject = None
        self.getNewProject = False

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 10

        # grid = QGridLayout()

        # buttonLayout = QVBoxLayout()

        layout = QVBoxLayout()

        self.projectTree = QTreeWidget()
        self.projectTree.setHeaderHidden(True)
        self.projectTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.projectTree.setFixedWidth(300)
        self.projectTree.setFixedHeight(300)
        self.projectTree.itemChanged.connect(self.projectTree_changed)
        self.projectTree.itemPressed.connect(self.projectTree_itemClicked)
        self.projectTree.itemClicked.connect(self.projectTree_itemClicked)
        self.projectTree.itemDoubleClicked.connect(self.ModifyProjectBtnClicked)
        # grid.addWidget(self.projectTree, 0, 1)
        layout.addWidget(self.projectTree, 0)

        self.projectTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.projectTree.customContextMenuRequested.connect(self.Show_context_menu)

        AddProjectBtn = QPushButton("Ajouter")
        AddProjectBtn.setFixedHeight(30)
        AddProjectBtn.setFixedWidth(100)
        AddProjectBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        AddProjectBtn.clicked.connect(self.AddProjectBtnClicked)
        # buttonLayout.addWidget(AddProjectBtn, 0)
        layout.addWidget(AddProjectBtn, 1, Qt.AlignCenter)

        # DelProjectBtn = QPushButton("Supprimer")
        # DelProjectBtn.setFixedHeight(30)
        # DelProjectBtn.setFixedWidth(100)
        # DelProjectBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        # DelProjectBtn.clicked.connect(self.DeleteProjectBtnClicked)
        # buttonLayout.addWidget(DelProjectBtn, 1)
        #
        # grid.addLayout(buttonLayout, 0, 0)



        self.Update_project_tree()

        # self.setLayout(grid)
        self.setLayout(layout)

    def keyPressEvent(self, e):
        if e.key() == 16777223:
            self.DeleteProjectBtnClicked()


    def Save(self):
        with open('projects.yaml', 'w') as f:
            yaml.dump(self.mainWin.projectList, f, sort_keys=False)

    def Update_project_tree(self):
        self.projectTree.clear()
        for project in self.mainWin.projectList:
            elmt = QTreeWidgetItem(self.projectTree)
            elmt.setFont(0, QFont('AnyStyle', self.subtitleFontSize))
            elmt.setText(0, project["Name"])

    def projectTree_itemClicked(self, item, col):
        if item.isSelected():
            self.selectedProject = item

    def projectTree_changed(self):
        pass

    def Show_context_menu(self, position):
        display_action1 = QAction("Modifier le projet")
        display_action1.triggered.connect(self.ModifyProjectBtnClicked)
        display_action2 = QAction("Supprimer le projet")
        display_action2.triggered.connect(self.DeleteProjectBtnClicked)

        menu = QMenu(self.projectTree)
        menu.addAction(display_action1)
        menu.addAction(display_action2)

        menu.exec_(self.projectTree.mapToGlobal(position))

    def ModifyProjectBtnClicked(self):
        initialProjectName = self.selectedProject.text(0)
        modifyInputDialog = QInputDialog(self)
        modifyInputDialog.setInputMode(QInputDialog.TextInput)
        modifyInputDialog.setWindowTitle('Modifier un projet')
        modifyInputDialog.setLabelText('Nom du projet :')
        modifyInputDialog.setTextValue(initialProjectName)
        modifyInputDialog.setFont(QFont('AnyStyle', self.subtitleFontSize))
        ok = modifyInputDialog.exec_()
        text = modifyInputDialog.textValue()
        if ok:
            for project in self.mainWin.projectList:
                if project["Name"] == initialProjectName:
                    project["Name"] = text
                    self.mainWin.modified_project.emit([initialProjectName, text])
                    break

        self.Save()
        self.Update_project_tree()

    def AddProjectBtnClicked(self):

        addInputDialog = QInputDialog(self)
        addInputDialog.setInputMode(QInputDialog.TextInput)
        addInputDialog.setWindowTitle('Entrer un projet')
        addInputDialog.setLabelText('Nom du projet :')
        addInputDialog.setFont(QFont('AnyStyle', 9))
        ok = addInputDialog.exec_()
        text = addInputDialog.textValue()
        # text, ok = QInputDialog.getText(self, 'Entrer un projet', 'Nom du projet :')
        if ok:
            self.mainWin.projectList.append({"Name": text})

        self.Save()
        self.Update_project_tree()

        if self.getNewProject and ok:
            self.getNewProject = False
            self.hide()
            self.mainWin.new_project.emit(text)

    def DeleteProjectBtnClicked(self):
        projectName = self.selectedProject.text(0)
        msg = QMessageBox()
        msg.setWindowTitle("Suppression d'un projet")
        msg.setText(f'Le projet "{projectName}" va être supprimé, ainsi que toutes les tâches associées')
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.buttonClicked.connect(self.onDeleteMsgBoxBtnClicked)

        msg.setButtonText(QMessageBox.Cancel, "Annuler")
        msg.setButtonText(QMessageBox.Ok, "OK")
        msg.exec_()

    def onDeleteMsgBoxBtnClicked(self, button):
        if button.text() == 'OK':
            projectToDelete = {"Name": self.selectedProject.text(0)}

            self.mainWin.delete_project.emit(self.selectedProject.text(0))

    def GetNewProject(self):
        self.getNewProject = True
        self.AddProjectBtnClicked()


# class MainWindow(QWidget):
class MainWindow(QMainWindow):

    new_task = Signal(object)
    modify_task = Signal(object)
    modified_task = Signal(object)

    modified_project = Signal(object)

    get_new_project = Signal()
    new_project = Signal(object)
    delete_project = Signal(object)

    def __init__(self):
        super().__init__()

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
        # self.setFixedWidth(1118)
        # self.setFixedHeight(550)
        self.setMinimumHeight(550)

        self.tasksList = []
        self.projectList = []
        self.selectedItem = None
        self.updating = False

        self.projectAscending = None
        self.startDateAscending = None
        self.endDateAscending = None
        self.waitForNotifications = 1800000  # msec  30min = 30*60*1000 = 1.800.000

        self.setWindowModality(Qt.ApplicationModal)

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

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 10

        # menu bar
        menu = self.menuBar()
        file = menu.addMenu("Fichier")
        file.addAction("Quitter", lambda: sys.exit(0))
        taskMenu = menu.addMenu("Tâches")
        taskMenu.addAction("Ajouter une tâche ...", lambda: self.AddTaskBtnClicked(), QKeySequence("a"))
        taskMenu.addAction("Supprimer une tâche", lambda: self.DeleteTaskBtnClicked(), QKeySequence.Delete)
        projectMenu = menu.addMenu("Projets")
        projectMenu.addAction("Gérer les projets ...", lambda: self.ManageProjectsBtnClicked())

        layout = QVBoxLayout()

        self.runningWidget = QWidget(self)
        runningLayout = QGridLayout()

        self.listTree = QTreeWidget(self)
        self.listTree.setHeaderLabels(["", "Nom", "Description", "Projets", "Début", "Fin"])
        self.listTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.listTree.setMinimumWidth(1090)
        self.listTree.setColumnWidth(0, 50)
        self.listTree.setColumnWidth(1, 200)
        self.listTree.setColumnWidth(2, 480)
        self.listTree.setColumnWidth(3, 120)
        self.listTree.setColumnWidth(4, 112)
        self.listTree.setColumnWidth(5, 112)
        # self.listTree.setStyleSheet("QTreeWidget::Item{border-bottom: 10px solid red}")
        # self.listTree.setStyleSheet("QTreeWidget::Item{padding: 5px}")
        # elmt.setStyleSheet("QTreeWidgetItem {margin: 20px}")

        self.listTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listTree.customContextMenuRequested.connect(self.Show_lists_context_menu)

        self.listTree.itemChanged.connect(self.listTree_changed)
        # self.listTree.itemClicked.connect(self.listTree_itemClicked)
        self.listTree.itemPressed.connect(self.listTree_itemClicked)
        self.listTree.itemDoubleClicked.connect(self.ModifyTaskBtnClicked)
        runningLayout.addWidget(self.listTree, 2, 0, 1, 4)

        self.listTreeHeader = self.listTree.header()
        self.listTreeHeader.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # self.listTreeHeader.setSectionResizeMode(QHeaderView.Fixed)
        self.listTreeHeader.setStretchLastSection(False)
        # self.listTreeHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.listTreeHeader.setSectionsClickable(True)
        self.listTreeHeader.sectionClicked.connect(self.customSortByColumn)

        self.runningWidget.setLayout(runningLayout)

        self.finishedWidget = QWidget(self)
        finishedLayout = QGridLayout()

        self.finishedTasksTree = QTreeWidget(self)
        self.finishedTasksTree.setHeaderLabels(["", "Nom", "Description", "Projets", "Début", "Fin"])
        self.finishedTasksTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.finishedTasksTree.setMinimumWidth(1090)
        self.finishedTasksTree.setColumnWidth(0, 50)
        self.finishedTasksTree.setColumnWidth(1, 200)
        self.finishedTasksTree.setColumnWidth(2, 480)
        self.finishedTasksTree.setColumnWidth(3, 120)
        self.finishedTasksTree.setColumnWidth(4, 112)
        self.finishedTasksTree.setColumnWidth(5, 112)
        self.finishedTasksTree.itemChanged.connect(self.finishedTasksTree_changed)
        # self.finishedTasksTree.itemClicked.connect(self.finishedTasksTree_itemClicked)
        self.finishedTasksTree.itemPressed.connect(self.finishedTasksTree_itemClicked)
        self.finishedTasksTree.itemDoubleClicked.connect(self.ModifyTaskBtnClicked)
        finishedLayout.addWidget(self.finishedTasksTree, 2, 0, 1, 4)

        self.finishedTasksTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.finishedTasksTree.customContextMenuRequested.connect(self.Show_lists_context_menu)

        self.finishedTasksTreeHeader = self.finishedTasksTree.header()
        self.finishedTasksTreeHeader.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.finishedTasksTreeHeader.setStretchLastSection(False)
        self.finishedTasksTreeHeader.setSectionsClickable(True)
        self.finishedTasksTreeHeader.sectionClicked.connect(self.customSortByColumn)


        self.finishedWidget.setLayout(finishedLayout)

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.runningWidget, "En cours")
        self.tabs.addTab(self.finishedWidget, "Terminées")

        layout.addWidget(self.tabs)

        main_window = QWidget()
        main_window.setLayout(layout)  # runningLayout
        self.setCentralWidget(main_window)
        # self.setLayout(runningLayout)

        self.Update_changes()

        self.notifyTimer = QTimer(self)
        self.notifyTimer.timeout.connect(self.NotifyUser)
        self.notifyTimer.start(self.waitForNotifications)

        self.new_task.connect(self.New_task)
        self.modify_task.connect(self.addTaskDialog.ModifyTask)
        self.modified_task.connect(self.ModifiedTask)
        self.get_new_project.connect(self.projectsDialog.GetNewProject)
        self.new_project.connect(self.New_project)
        self.delete_project.connect(self.DeleteProject)
        self.modified_project.connect(self.ModifiedProject)

        self.show()
        self.NotifyUser()

    def keyPressEvent(self, e):
        pass
        # if e.key() == 16777223:
        #     self.DeleteTaskBtnClicked()

    def Save(self):
        with open('tasks.yaml', 'w') as f:
            yaml.dump(self.tasksList, f, sort_keys=False)

    def New_task(self, task):
        self.tasksList.append(task)

        self.Save()
        self.Update_changes()

    def Update_changes(self):
        time.sleep(0.1)
        self.listTree.clearFocus()
        self.finishedTasksTree.clearFocus()
        self.listTree.clearSelection()
        self.finishedTasksTree.clearSelection()
        self.listTree.clear()
        self.finishedTasksTree.clear()
        i = 0
        iRunning = 0
        iFinished = 0
        runningTasksNb = 0
        finishedTasksNb = 0
        tree_to_build = None
        tree_len = 0

        for task in self.tasksList:
            if task["Check"] == 0:
                runningTasksNb += 1
            elif task["Check"] == 1:
                finishedTasksNb += 1

        self.updating = True

        if self.tasksList is not None:
            for task in self.tasksList:

                if task["Check"] == 0:
                    tree_to_build = self.listTree
                    iRunning += 1
                    i = iRunning
                    tree_len = runningTasksNb
                elif task["Check"] == 1:
                    tree_to_build = self.finishedTasksTree
                    iFinished += 1
                    i = iFinished
                    tree_len = finishedTasksNb

                elmt = QTreeWidgetItem(tree_to_build)
                elmt.setFlags(elmt.flags() | Qt.ItemIsUserCheckable)

                lbl = QLabel(f'\n{task["Name"]}\n')
                # lbl = QLabel(task["Name"])
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 1, lbl)

                lbl = QLabel(f'\n{task["Description"]}\n')
                # lbl = QLabel(task["Description"])
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setMaximumWidth(500)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 2, lbl)

                lbl = QLabel(task["Project"])
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 3, lbl)

                try:
                    year, month, day = task["StartDate"].split("-")
                    date = f'{day}/{month}/{year}'
                except:
                    date = task["StartDate"]

                lbl = QLabel(date)
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 4, lbl)

                try:
                    year, month, day = task["EndDate"].split("-")
                    date = f'{day}/{month}/{year}'
                except:
                    date = task["EndDate"]

                lbl = QLabel(date)
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 5, lbl)

                # if i < tree_len:
                #     spacer = QTreeWidgetItem(tree_to_build)
                #     spacer.setFlags(Qt.NoItemFlags)
                #
                #     lbl = QLabel("")
                #     lbl.setFont(QFont('AnyStyle', 1))
                #
                #     tree_to_build.setItemWidget(spacer, 0, lbl)

                if task["Check"] == 1:
                    elmt.setCheckState(0, Qt.Checked)
                else:
                    elmt.setCheckState(0, Qt.Unchecked)

        self.updating = False

    def finishedTasksTree_changed(self, item, col):
        try:
            if not self.updating:
                # if item.checkState(0) == Qt.Checked:
                #     for task in self.tasksList:
                #         if task["Name"] == self.finishedTasksTree.itemWidget(item, 1).text() and \
                #                 task["Description"] == self.finishedTasksTree.itemWidget(item, 2).text():
                #             task["Check"] = 1
                #             break

                if item.checkState(0) == Qt.Unchecked:
                    for task in self.tasksList:
                        if f'\n{task["Name"]}\n' == self.finishedTasksTree.itemWidget(item, 1).text() and \
                                f'\n{task["Description"]}\n' == self.finishedTasksTree.itemWidget(item, 2).text():
                        # if task["Name"] == self.finishedTasksTree.itemWidget(item, 1).text() and \
                        #         task["Description"] == self.finishedTasksTree.itemWidget(item, 2).text():
                            task["Check"] = 0
                            break

                self.Save()
                self.Update_changes()
        except Exception as e:
            print("finishedTasksTree_changed:", e)

    def listTree_changed(self, item, col):
        try:
            if not self.updating:
                if item.checkState(0) == Qt.Checked:
                    for task in self.tasksList:
                        if f'\n{task["Name"]}\n' == self.listTree.itemWidget(item, 1).text() and \
                                 f'\n{task["Description"]}\n' == self.listTree.itemWidget(item, 2).text():
                        # if task["Name"] == self.listTree.itemWidget(item, 1).text() and \
                        #         task["Description"] == self.listTree.itemWidget(item, 2).text():
                            task["Check"] = 1
                            break

                # elif item.checkState(0) == Qt.Unchecked:
                #     for task in self.tasksList:
                #         if task["Name"] == self.listTree.itemWidget(item, 1).text() and \
                #                 task["Description"] == self.listTree.itemWidget(item, 2).text():
                #             task["Check"] = 0
                #             break

                self.Save()
                self.Update_changes()
        except Exception as e:
            print("listTree_changed:", e)

    def listTree_itemClicked(self, item, col):
        try:
            if item.isSelected():
                self.selectedItem = item
        except Exception as e:
            print("listTree_itemClicked", e)

    def finishedTasksTree_itemClicked(self, item, col):
        try:
            if item.isSelected():
                self.selectedItem = item
        except Exception as e:
            print("finishedTasksTree_itemClicked", e)

    def Update_project_combo_box(self):
        self.addTaskDialog.projectComboBox.clear()
        for i in range(0, len(self.projectList)):
            self.addTaskDialog.projectComboBox.insertItem(i, self.projectList[i]["Name"])
        self.addTaskDialog.projectComboBox.insertItem(len(self.projectList), "--Nouveau--")

    def AddTaskBtnClicked(self):
        self.Update_project_combo_box()
        self.addTaskDialog.show()

    def ModifyTaskBtnClicked(self):
        self.Update_project_combo_box()

        current_tree = self.SelectedTree()

        taskToModify = self.getTask(current_tree)

        self.modify_task.emit(taskToModify)

        # for task in self.tasksList:
        #     if f'\n{task["Name"]}\n' == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #             f'\n{task["Description"]}\n' == current_tree.itemWidget(self.selectedItem, 2).text():
        #     # if task["Name"] == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #     #         task["Description"] == current_tree.itemWidget(self.selectedItem, 2).text():
        #         self.modify_task.emit(task)
        #         break

    def ModifiedTask(self, modifiedTask):

        current_tree = self.SelectedTree()

        task = self.getTask(current_tree)

        task["Name"] = modifiedTask["Name"]
        task["Description"] = modifiedTask["Description"]
        task["Project"] = modifiedTask["Project"]
        task["StartDate"] = modifiedTask["StartDate"]
        task["EndDate"] = modifiedTask["EndDate"]

        # for task in self.tasksList:
        #     if f'\n{task["Name"]}\n' == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #             f'\n{task["Description"]}\n' == current_tree.itemWidget(self.selectedItem, 2).text():
        #     # if task["Name"] == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #     #         task["Description"] == current_tree.itemWidget(self.selectedItem, 2).text():
        #         task["Name"] = modifiedTask["Name"]
        #         task["Description"] = modifiedTask["Description"]
        #         task["Project"] = modifiedTask["Project"]
        #         task["StartDate"] = modifiedTask["StartDate"]
        #         task["EndDate"] = modifiedTask["EndDate"]
        #         break

        self.Save()
        self.Update_changes()

    def DeleteTaskBtnClicked(self):

        current_tree = self.SelectedTree()

        try:
            taskName = current_tree.itemWidget(self.selectedItem, 1).text()

            taskName = taskName.replace("\n", "")

            msg = QMessageBox()
            msg.setWindowTitle("Suppression d'une tâche")
            msg.setText(f'La tache "{taskName}" va être supprimée')
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.onDeleteMsgBoxBtnClicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Suppression d'une tâche")
            msg.setText(f"Aucune tâche sélectionnée")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec_()

    def onDeleteMsgBoxBtnClicked(self, button):
        if button.text() == 'OK':

            current_tree = self.SelectedTree()

            # taskToDelete = None

            taskToDelete = self.getTask(current_tree)

            # for task in self.tasksList:
            #     # if f'\n{task["Name"]}\n' == current_tree.itemWidget(self.selectedItem, 1).text() and \
            #     #         f'\n{task["Description"]}\n' == current_tree.itemWidget(self.selectedItem, 2).text():
            #     if task["Name"] == current_tree.itemWidget(self.selectedItem, 1).text() and \
            #             task["Description"] == current_tree.itemWidget(self.selectedItem, 2).text():
            #         taskToDelete = task
            #         break

            self.tasksList.remove(taskToDelete)

            self.Save()
            self.Update_changes()

    def getTask(self, tree):
        for task in self.tasksList:
            if f'\n{task["Name"]}\n' == tree.itemWidget(self.selectedItem, 1).text() and \
                    f'\n{task["Description"]}\n' == tree.itemWidget(self.selectedItem, 2).text():
            # if task["Name"] == tree.itemWidget(self.selectedItem, 1).text() and \
            #         task["Description"] == tree.itemWidget(self.selectedItem, 2).text():
                return task


    def ManageProjectsBtnClicked(self):
        self.projectsDialog.show()

    def New_project(self, received_object):
        self.Update_project_combo_box()

        self.addTaskDialog.projectComboBox.setCurrentText(received_object)

    def DeleteProject(self, received_object):
        projectName = received_object
        tasks = []

        for task in self.tasksList:
            if projectName == task["Project"]:
                tasks.append(task)

        for task in tasks:
            self.tasksList.remove(task)

        self.Save()
        self.Update_changes()

        self.projectList.remove({"Name": projectName})

        self.projectsDialog.Save()
        self.projectsDialog.Update_project_tree()

    def customSortByColumn(self, column):
        if column == 3:
            if self.projectAscending is None or not self.projectAscending:
                self.tasksList.sort(key=lambda x: x.get("Project"))
                self.projectAscending = True
            else:
                self.tasksList.sort(key=lambda x: x.get("Project"), reverse=True)
                self.projectAscending = False

        elif column == 4:
            if self.startDateAscending is None or not self.startDateAscending:
                self.tasksList.sort(key=lambda x: x.get("StartDate"))
                self.startDateAscending = True
            else:
                self.tasksList.sort(key=lambda x: x.get("StartDate"), reverse=True)
                self.startDateAscending = False
        elif column == 5:
            if self.endDateAscending is None or not self.endDateAscending:
                self.tasksList.sort(key=lambda x: x.get("EndDate"))
                self.endDateAscending = True
            else:
                self.tasksList.sort(key=lambda x: x.get("EndDate"), reverse=True)
                self.endDateAscending = False

        self.Save()
        self.Update_changes()

    def SelectedTree(self):
        if self.tabs.currentWidget() == self.runningWidget:
            return self.listTree
        elif self.tabs.currentWidget() == self.finishedWidget:
            return self.finishedTasksTree

    def Show_lists_context_menu(self, position):
        display_action1 = QAction("Modifier la tâche")
        display_action1.triggered.connect(self.ModifyTaskBtnClicked)
        display_action2 = QAction("Supprimer la tâche")
        display_action2.triggered.connect(self.DeleteTaskBtnClicked)

        menu = QMenu(self.listTree)
        menu.addAction(display_action1)
        menu.addAction(display_action2)

        menu.exec_(self.listTree.mapToGlobal(position))

    def ModifiedProject(self, data):
        initial_project_name = data[0]
        new_project_name = data[1]

        for task in self.tasksList:
            if task["Project"] == initial_project_name:
                task["Project"] = new_project_name

        self.Save()
        self.Update_changes()

    def NotifyUser(self):

        today = QDate.currentDate()

        date = QDate()
        date.setDate(QDate.year(today), QDate.month(today), QDate.day(today))
        dayNumber = date.dayOfWeek()

        endOfWeek = today.addDays(7-dayNumber)

        todayDay, todayMonth, todayYear = today.toString(Qt.ISODate).split("-")
        todayStr = todayDay + todayMonth + todayYear
        endOfWeekDay, endOfWeekMonth, endOfWeekYear = endOfWeek.toString(Qt.ISODate).split("-")
        endOfWeekStr = endOfWeekDay + endOfWeekMonth + endOfWeekYear

        passedList = []
        passedList.append("TÂCHES DONT LE DÉLAI EST DÉPASSÉ :")

        todayList = []
        todayList.append("Voici les tâches à accomplir aujourd'hui :")

        endOfWeekList = []
        endOfWeekList.append("Voici les tâches à accomplir cette semaine :")

        for task in self.tasksList:
            if task["Check"] == 0:
                try:
                    taskEndDateDay, taskEndDateMonth, taskEndDateYear = task["EndDate"].split("-")
                    taskEndDate = taskEndDateDay + taskEndDateMonth + taskEndDateYear

                    if taskEndDate < todayStr:
                        passedList.append(f' - {task["Name"]}')
                    elif taskEndDate == todayStr:
                        todayList.append(f' - {task["Name"]}')
                    elif taskEndDate <= endOfWeekStr:
                        endOfWeekList.append(f' - {task["Name"]}')
                except:
                    pass  # no end date

        notificationText = ""

        if len(passedList) > 1:
            for line in passedList:
                notificationText += ("\n" + line)
            notificationText += "\n"

        if len(todayList) > 1:
            for line in todayList:
                notificationText += ("\n" + line)
            notificationText += "\n"

        if len(endOfWeekList) > 1:
            for line in endOfWeekList:
                notificationText += ("\n" + line)

        if len(passedList) == 1 and len(todayList) == 1 and len(endOfWeekList) == 1:
            notificationText = "Vous êtes à jour pour cette semaine"

        msg = QMessageBox()
        msg.setWindowTitle("Vos tâches")
        msg.setText(notificationText)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setButtonText(QMessageBox.Ok, "OK")
        msg.setDefaultButton(QMessageBox.Ok)
        self.notifyTimer.stop()
        msg.exec_()
        self.notifyTimer.start(self.waitForNotifications)

if __name__ == "__main__":
    app = QApplication([])

    style(app)

    mainWindow = MainWindow()
    sys.exit(app.exec_())
