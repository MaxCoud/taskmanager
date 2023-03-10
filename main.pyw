import os
import sys
import shutil
import time
from style import style

from pathlib import Path
from add_window import AddTaskDialog
from project_window import ProjectsDialog

import yaml
from PySide2.QtCore import Qt, Signal, QDateTime, QDate, QTimer, QModelIndex
from PySide2.QtGui import QFont, QTextOption, QKeySequence, QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QWidget, QApplication, QLabel, QPushButton, \
    QCheckBox, QTreeWidget, QTreeWidgetItem, QDateEdit, QDialog, QVBoxLayout, QPlainTextEdit, QMessageBox, \
    QInputDialog, QComboBox, QTabWidget, QAction, QMainWindow, QMenu, QTreeView, QHeaderView


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

        # change working directory to this script directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        d = os.getcwd()

        # linux shortcut
        if self.os == 'linux':
            self.slash = "/"

            path = os.fspath(Path(__file__).resolve().parent / "taskmanager.desktop")
            if not os.path.exists(path):
                f = open(path, 'w')
                f.write('[Desktop Entry]\n')
                f.write('Name=Task Manager\n')
                f.write(f'Name={d}/task_manager_logo1.png\n')
                f.write(f'Exec=/usr/bin/python3 --working-directory={d}/ {d}/main.py\n')
                f.write('Terminal=false\n')
                f.write('Type=Application\n')
                f.close()

        elif self.os == 'windows' or self.os == 'win32':
            self.slash = "\\"

        self.setWindowTitle("Task Manager")
        # self.setFixedWidth(1118)
        # self.setFixedHeight(550)
        self.setMinimumHeight(750)

        self.tasksList = None
        self.projectList = []
        self.selectedItem = None
        self.parent_list = None
        self.selectedProject = None
        self.selected_project_tasks_list = None
        self.updating = False

        # self.projectAscending = None
        self.priorityAscending = None
        self.startDateAscending = None
        self.endDateAscending = None
        self.waitForNotifications = 1800000  # msec  30min = 30*60*1000 = 1.800.000

        self.setWindowModality(Qt.ApplicationModal)

        self.task_tree = []

        try:
            with open(f'{d}{self.slash}tasks_tree.yaml', 'r') as f:
                self.task_tree = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open(f'{d}{self.slash}tasks_tree.yaml', 'w') as f:
                yaml.dump(None, f, sort_keys=False)

        # try:
        #     with open(f'{d}{self.slash}tasks.yaml', 'r') as f:
        #         self.tasksList = yaml.load(f, Loader=yaml.FullLoader)
        # except FileNotFoundError:
        #     with open(f'{d}{self.slash}tasks.yaml', 'w') as f:
        #         yaml.dump(None, f, sort_keys=False)

        try:
            with open(f'{d}{self.slash}projects.yaml', 'r') as f:
                self.projectList = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            with open(f'{d}{self.slash}projects.yaml', 'w') as f:
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

        layout = QGridLayout()

        self.runningWidget = QWidget(self)
        runningLayout = QGridLayout()

        self.tree_view = QTreeView(self)
        self.tree_view.setMinimumWidth(300)
        # self.tree_view.clicked.connect(self.OnProjectTreeClicked)
        self.tree_view.pressed.connect(self.OnProjectTreeClicked)
        layout.addWidget(self.tree_view, 0, 0)

        # create a model for tree view
        self.model = QStandardItemModel()

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.Show_tree_context_menu)

        # get header of tree view
        self.tree_view_header = self.tree_view.header()
        # self.tree_view_header.setSectionResizeMode(QHeaderView.Interactive)

        newProjectBtn = QPushButton("Ajouter un projet", self)
        newProjectBtn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        newProjectBtn.setFixedHeight(30)
        newProjectBtn.clicked.connect(self.AddProjectButtonClicked)
        layout.addWidget(newProjectBtn, 1, 0)

        self.listTree = QTreeWidget(self)
        self.listTree.setHeaderLabels(["", "Nom", "Description", "Priorité", "Début", "Fin", "Documents"])
        self.listTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.listTree.setMinimumWidth(1256)
        self.listTree.setColumnWidth(0, 50)
        self.listTree.setColumnWidth(1, 200)
        self.listTree.setColumnWidth(2, 480)
        self.listTree.setColumnWidth(3, 200)
        self.listTree.setColumnWidth(4, 112)
        self.listTree.setColumnWidth(5, 112)
        self.listTree.setColumnWidth(6, 100)
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
        self.finishedTasksTree.setHeaderLabels(["", "Nom", "Description", "Priorité", "Début", "Fin", "Documents"])
        self.finishedTasksTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.finishedTasksTree.setMinimumWidth(1256)
        self.finishedTasksTree.setColumnWidth(0, 50)
        self.finishedTasksTree.setColumnWidth(1, 200)
        self.finishedTasksTree.setColumnWidth(2, 480)
        self.finishedTasksTree.setColumnWidth(3, 200)
        self.finishedTasksTree.setColumnWidth(4, 112)
        self.finishedTasksTree.setColumnWidth(5, 112)
        self.finishedTasksTree.setColumnWidth(6, 100)
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

        layout.addWidget(self.tabs, 0, 1, 2, 1)

        main_window = QWidget()
        main_window.setLayout(layout)  # runningLayout
        self.setCentralWidget(main_window)
        # self.setLayout(runningLayout)

        # --- Message box management ---
        self.no_task_msg = QMessageBox(self)
        self.no_task_msg.setWindowTitle("Information")
        self.no_task_msg.setText("Pas de tâches dans cette section")
        self.no_task_msg.setFont(QFont("Arial", 12))
        self.no_task_msg.setIcon(QMessageBox.Information)
        self.no_task_msg_timer = QTimer(self)
        self.no_task_msg_timeout = 1000  # msec
        self.no_task_msg_timer.timeout.connect(self.no_task_msg_timer_timeout)

        self.Update_changes()
        self.Update_tree()

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

    def Update_tree(self):

        self.model.clear()

        def add_item(parent, data):
            item = QStandardItem(data['Name'])
            item.setData(data)
            item.setEditable(False)
            parent.appendRow(item)
            if 'Children' in data:
                for child in data['Children']:
                    # add_item(item, child)
                    # if not 'Description' in child:
                    if 'Children' in child or not 'Description' in child:
                        add_item(item, child)


        # create the root item and add it to the model
        root_item = QStandardItem(self.task_tree['Name'])
        root_item.setData(self.task_tree)
        self.model.appendRow(root_item)

        # set label of tree header with root name
        self.model.setHorizontalHeaderLabels([self.task_tree['Name']])

        # self.model.invisibleRootItem().child(0,0).index()
        # self.tree_view.setRootIndex(self.model.invisibleRootItem().child(0).index())

        # add child items recursively
        if 'Children' in self.task_tree:
            for child in self.task_tree['Children']:
                # add_item(root_item, child)
                # if not 'Description' in child:
                if 'Name' in child and not 'Description' in child:
                    add_item(root_item, child)

        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()

        # hide root element
        self.tree_view.setRootIndex(self.model.index(0, 0))

        # self.tree_view_header.setStretchLastSection(False)
        # self.tree_view_header.setSectionResizeMode(0, QHeaderView.Interactive)
        # self.tree_view_header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_view_header.resizeSection(0, self.tree_view.sizeHintForColumn(0))
        # self.tree_view_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # self.tree_view.setHeaderHidden(True)

        # hide triangle
        # self.tree_view.setRootIsDecorated(False)

    def OnProjectTreeClicked(self, index):
        item = self.model.itemFromIndex(index)
        print(item.text())

        hasParent = True
        self.parent_list = [item.text()]
        child = item

        while hasParent:
            try:
                parent = child.parent()
                self.parent_list.append(parent.text())
                child = parent
            except:
                hasParent = False

        print("parent_list", self.parent_list)

        parent_name = self.task_tree['Name']
        # parent_ = self.task_tree['Children'][0]
        parent_ = self.task_tree
        tasks_list = None

        if parent_name == self.parent_list[len(self.parent_list)-1]:
            for i in range(len(self.parent_list), 0, -1):
                for child in parent_["Children"]:
                    if child['Name'] == self.parent_list[i-1]:
                        parent_ = child
                        if (i-1) == 0:  # last element
                            # try:
                            #     # if first element of child['Children'] (= task list) has no description, it can be
                            #     # a task list, there is at least one level below
                            #     desc = child['Children'][0]['Description']
                            #     tasks_list = child
                            # except:
                            #     pass

                            tasks_list = child

                            break

        if tasks_list is not None:
            self.selected_project_tasks_list = tasks_list['Children']
        else:
            self.selected_project_tasks_list = None

        self.tasksList = self.selected_project_tasks_list
        self.Update_changes()

        self.selectedProject = item

    def Show_tree_context_menu(self, position):
        add_section = QAction("Ajouter une section")
        add_section.triggered.connect(self.AddProjectSectionButtonClicked)
        modify_section = QAction("Modifier")
        modify_section.triggered.connect(self.ModifySectionButtonClicked)
        delete_section = QAction("Supprimer")
        delete_section.triggered.connect(self.RemoveSectionButtonClicked)

        menu = QMenu(self.tree_view)
        menu.addAction(add_section)
        menu.addAction(modify_section)
        menu.addAction(delete_section)

        menu.exec_(self.tree_view.mapToGlobal(position))

    def AddProjectButtonClicked(self):
        addProjectDialog = QInputDialog(self)
        addProjectDialog.setInputMode(QInputDialog.TextInput)
        addProjectDialog.setWindowTitle('Entrer un projet global')
        addProjectDialog.setLabelText('Nom du projet :')
        addProjectDialog.setFont(QFont('AnyStyle', 9))
        ok = addProjectDialog.exec_()
        text = addProjectDialog.textValue()

        if ok:
            self.task_tree["Children"].append({"Name": text})

        self.Save_tree()
        self.Update_tree()

    def AddProjectSectionButtonClicked(self):

        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element
                                addSectionDialog = QInputDialog(self)
                                addSectionDialog.setInputMode(QInputDialog.TextInput)
                                addSectionDialog.setWindowTitle('Entrer une section')
                                addSectionDialog.setLabelText('Nom de la section :')
                                addSectionDialog.setFont(QFont('AnyStyle', 9))
                                ok = addSectionDialog.exec_()
                                text = addSectionDialog.textValue()

                                if ok:
                                    if 'Children' in child:
                                        child['Children'].append({"Name": text})
                                    else:
                                        child['Children'] = []
                                        child['Children'].append({"Name": text})

                                self.Save_tree()
                                self.Update_tree()
                                self.Update_changes()

    def ModifySectionButtonClicked(self):
        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element
                                modifySectionDialog = QInputDialog(self)
                                modifySectionDialog.setInputMode(QInputDialog.TextInput)
                                modifySectionDialog.setWindowTitle('Modifier une section')
                                modifySectionDialog.setLabelText('Nouveau nom de la section :')
                                lineEdit = modifySectionDialog.findChild(QLineEdit)
                                lineEdit.setPlaceholderText(f'{child["Name"]}')
                                modifySectionDialog.setFont(QFont('AnyStyle', 9))
                                ok = modifySectionDialog.exec_()
                                text = modifySectionDialog.textValue()

                                if ok:
                                    child['Name'] = text

                                self.Save_tree()
                                self.Update_tree()
                                self.Update_changes()

    def RemoveSectionButtonClicked(self):

        msg = QMessageBox()
        msg.setWindowTitle("Suppression d'une section")
        msg.setText(f'La section "{self.selectedProject.text()}" va être supprimée,\n'
                    f'ainsi que toutes les potentielles sous sections\n'
                    f'et tâches lui appartenant.')
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.buttonClicked.connect(self.onDeleteSectionMsgBoxBtnClicked)

        msg.setButtonText(QMessageBox.Cancel, "Annuler")
        msg.setButtonText(QMessageBox.Ok, "OK")
        msg.exec_()

    def onDeleteSectionMsgBoxBtnClicked(self, button):
        if button.text() == 'OK':

            if self.parent_list is not None:
                parent_name = self.task_tree['Name']
                parent_ = self.task_tree

                if parent_name == self.parent_list[len(self.parent_list) - 1]:
                    for i in range(len(self.parent_list), 0, -1):
                        for child in parent_["Children"]:
                            if child['Name'] == self.parent_list[i - 1]:

                                if (i - 1) == 0:  # last element

                                    parent_["Children"].remove(child)

                                    self.Save_tree()
                                    self.Update_tree()
                                    self.Update_changes()

                                parent_ = child

    def Remove_task(self, taskToDelete):

        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element

                                if 'Children' in child:
                                    child['Children'].remove(taskToDelete)

                                    self.Save_tree()
                                    self.Update_tree()
                                    self.Update_changes()


    def Save_tree(self):
        with open('tasks_tree.yaml', 'w') as f:
            yaml.dump(self.task_tree, f, sort_keys=False)

    def Save(self):
        with open('tasks.yaml', 'w') as f:
            yaml.dump(self.tasksList, f, sort_keys=False)

    def New_task(self, task):
        # self.tasksList.append(task)

        print(self.tasksList)
        # if 'Children' in self.task_tree:
        #     self.task_tree['Children'].append(task)
        # else:
        #     self.task_tree['Children'] = []
        #     self.task_tree['Children'].append(task)

        # self.Save()


        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element

                                if 'Children' in child:
                                    child['Children'].append(task)
                                else:
                                    child['Children'] = []
                                    child['Children'].append(task)

                                self.tasksList = child['Children']

                                self.Save_tree()
                                self.Update_tree()
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

        self.updating = True

        if self.tasksList is not None:
            newTasksList = []
            for task in self.tasksList:
                if "Children" not in task:
                    newTasksList.append(task)
            self.tasksList = newTasksList

            for task in self.tasksList:
                if task["Check"] == 0:
                    runningTasksNb += 1
                elif task["Check"] == 1:
                    finishedTasksNb += 1
        else:
            self.no_task_msg.show()
            self.no_task_msg_timer.start(self.no_task_msg_timeout)
            self.no_task_msg_timer.timeout.connect(self.no_task_msg_timer_timeout)

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

                # lbl = QLabel(f'\n{task["Name"]}\n')
                lbl = QLabel(f'\n{task["Name"]}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 1, lbl)

                lbl = QLabel(f'\n{task["Description"]}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setMaximumWidth(500)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                tree_to_build.setItemWidget(elmt, 2, lbl)

                # lbl = QLabel(task["Project"])
                lbl = QLabel(task["Priority"])
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

    def no_task_msg_timer_timeout(self):
        self.no_task_msg_timer.stop()
        self.no_task_msg.close()

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

                # self.Save()
                self.Save_tree()
                self.Update_tree()
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

                # self.Save()
                self.Save_tree()
                self.Update_tree()
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
        # self.Update_project_combo_box()
        self.addTaskDialog.show()

    def ModifyTaskBtnClicked(self):
        # self.Update_project_combo_box()

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
        # task["Project"] = modifiedTask["Project"]
        task["Priority"] = modifiedTask["Priority"]
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

        # self.Save()
        self.Save_tree()
        self.Update_tree()
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

            self.Remove_task(taskToDelete)

            # # self.Save()
            # self.Save_tree()
            # self.Update_tree()
            # self.Update_changes()

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
        # self.Update_project_combo_box()

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
            # if self.projectAscending is None or not self.projectAscending:
            #     self.tasksList.sort(key=lambda x: x.get("Project"))
            #     self.projectAscending = True
            # else:
            #     self.tasksList.sort(key=lambda x: x.get("Project"), reverse=True)
            #     self.projectAscending = False
            if self.priorityAscending is None or not self.priorityAscending:
                self.tasksList.sort(key=lambda x: x.get("Priority"))
                self.priorityAscending = True
            else:
                self.tasksList.sort(key=lambda x: x.get("Priority"), reverse=True)
                self.priorityAscending = False

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

        # self.Save()
        self.Update_changes()

    def SelectedTree(self):
        if self.tabs.currentWidget() == self.runningWidget:
            return self.listTree
        elif self.tabs.currentWidget() == self.finishedWidget:
            return self.finishedTasksTree

    def Show_lists_context_menu(self, position):
        modify_action = QAction("Modifier la tâche")
        modify_action.triggered.connect(self.ModifyTaskBtnClicked)
        delete_action = QAction("Supprimer la tâche")
        delete_action.triggered.connect(self.DeleteTaskBtnClicked)

        menu = QMenu(self.listTree)
        menu.addAction(modify_action)
        menu.addAction(delete_action)

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

        if self.tasksList is not None:
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
