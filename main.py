import os
import sys
import shutil
import time
import markdown

from lib.style import style, select_icon, load_icons
import subprocess

from pathlib import Path
from lib.add_window import AddTaskDialog
from lib.param_window import *

import yaml
from PySide6.QtCore import Qt, QDateTime, QDate, QTimer
from PySide6.QtGui import QFont, QKeySequence, QStandardItem, QStandardItemModel, QIcon, QGuiApplication, \
    QCursor, QAction
from PySide6.QtWidgets import QLineEdit, QGridLayout, QWidget, QApplication, QLabel, QTreeWidget, QTreeWidgetItem, \
    QMessageBox, QInputDialog, QTabWidget, QMainWindow, QMenu, QTreeView
from PySide6.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.os = sys.platform
        path1 = os.fspath(Path(__file__).resolve().parent / "main.py")
        path2 = os.fspath(Path(__file__).resolve().parent / "main.pyw")
        shutil.copyfile(path1, path2)

        # change working directory to this script directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.d = os.getcwd()

        # linux shortcut
        if self.os == 'linux':
            self.slash = "/"

            path = os.fspath(Path(__file__).resolve().parent / "taskmanager.desktop")
            if not os.path.exists(path):
                f = open(path, 'w')
                f.write('[Desktop Entry]\n')
                f.write('Name=Task Manager\n')
                f.write(f'Name={self.d}/task_manager_logo.png\n')
                f.write(f'Exec=/usr/bin/python3 --working-directory={self.d}/ {self.d}/main.py\n')
                f.write('Terminal=false\n')
                f.write('Type=Application\n')
                f.close()

        elif self.os == 'windows' or self.os == 'win32':
            self.slash = "\\"

        self.setWindowTitle("Task Manager")
        # self.setFixedWidth(1118)
        # self.setFixedHeight(550)
        # self.setMinimumHeight(750)

        self.tasksList = None
        self.projectList = []
        self.selectedItem = None
        self.parent_list = None
        self.selectedProject = None
        self.selected_project_tasks_list = None
        self.updating = False
        self.copied_task = {}

        # self.projectAscending = None
        self.priorityAscending = None
        self.startDateAscending = None
        self.endDateAscending = None
        self.ts = time.time()  # store timestamp

        self.task_tree = []

        # icons
        self.icons = load_icons(Path(__file__).resolve().parent)

        self.app_logo = QIcon(f"{self.d}/task_manager_logo.png")
        self.setWindowIcon(self.app_logo)
        self.setWindowModality(Qt.ApplicationModal)

        if os.path.exists(f'{self.d}{self.slash}tasks_tree.yaml'):
            with open(f'{self.d}{self.slash}tasks_tree.yaml', 'r') as f:
                self.task_tree = yaml.load(f, Loader=yaml.FullLoader)
        else:
            with open(f'{self.d}{self.slash}tasks_tree.yaml', 'w') as f:
                new_task_tree = {
                    "Name": "Projects and subprojects",
                    "Children": [{
                        "Name": "example section",
                        "Children": [{
                            "Name": "example",
                            "Check": 0,
                            "Description": "example",
                            "Priority": "Urgent",
                            "StartDate": '2023-02-28',
                            "EndDate": '2023-03-10',
                            "Documents": []
                        }]
                    }]
                }
                yaml.dump(new_task_tree, f, sort_keys=False)
                self.task_tree = new_task_tree

        self.addTaskDialog = AddTaskDialog(self)
        self.param_dialog = ParamDialog(self)

        self.config = open_config_file(working_dir=self.d, slash=self.slash)

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 10

        # menu bar
        menu = self.menuBar()
        file = menu.addMenu("File")
        file.addAction("Quitter", lambda: sys.exit(0))

        task_menu = menu.addMenu("Tasks")
        task_menu.addAction("Add task ...", lambda: self.add_task_btn_clicked(), QKeySequence("a"))
        task_menu.addAction("Delete task", lambda: self.delete_task_btn_clicked(), QKeySequence.Delete)

        project_menu = menu.addMenu("Sections")
        project_menu.addAction("Add section", lambda: self.add_section_btn_clicked(), QKeySequence("s"))
        project_menu.addAction("Expand sections tree", lambda: self.expand_section_tree(),
                               QKeySequence(Qt.CTRL | Qt.ALT | Qt.Key_Plus))
        project_menu.addAction("Collapse sections tree", lambda: self.collapse_section_tree(),
                               QKeySequence(Qt.CTRL | Qt.ALT | Qt.Key_Minus))

        option_menu = menu.addMenu("Options")
        option_menu.addAction("Settings...", lambda: self.open_param_btn_clicked())

        layout = QGridLayout()

        self.runningWidget = QWidget()
        running_layout = QGridLayout()

        self.tree_view = QTreeView()
        self.tree_view.setMinimumWidth(300)
        # self.tree_view.clicked.connect(self.OnProjectTreeClicked)
        self.tree_view.pressed.connect(self.on_project_tree_clicked)
        layout.addWidget(self.tree_view, 0, 0, 4, 1)

        # create a model for tree view
        self.model = QStandardItemModel()

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_tree_context_menu)

        # get header of tree view
        self.tree_view_header = self.tree_view.header()
        # self.tree_view_header.setSectionResizeMode(QHeaderView.Interactive)

        self.selectedProjectLbl = QLabel()
        self.selectedProjectLbl.setText("No project selected")
        self.selectedProjectLbl.setFont(QFont('AnyStyle', self.titleFontSize))
        self.selectedProjectLbl.setFixedHeight(30)
        self.selectedProjectLbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selectedProjectLbl, 0, 1)

        self.listTree = QTreeWidget()
        self.listTree.setHeaderLabels(["", "Name", "Description", "Priority", "Start", "End", "Documents"])
        self.listTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.listTree.setMinimumWidth(1256)
        self.listTree.setMinimumHeight(550)
        self.listTree.setColumnWidth(0, 50)
        self.listTree.setColumnWidth(1, 200)
        self.listTree.setColumnWidth(2, 480)
        self.listTree.setColumnWidth(3, 200)
        self.listTree.setColumnWidth(4, 112)
        self.listTree.setColumnWidth(5, 112)
        self.listTree.setColumnWidth(6, 100)

        self.listTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listTree.customContextMenuRequested.connect(self.show_lists_context_menu)

        self.listTree.itemChanged.connect(self.list_tree_changed)
        # self.listTree.itemClicked.connect(self.listTree_itemClicked)
        self.listTree.itemPressed.connect(self.list_tree_item_clicked)
        self.listTree.itemDoubleClicked.connect(self.modify_task_btn_clicked)
        running_layout.addWidget(self.listTree, 2, 0, 1, 4)

        self.listTreeHeader = self.listTree.header()
        self.listTreeHeader.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # self.listTreeHeader.setSectionResizeMode(QHeaderView.Fixed)
        self.listTreeHeader.setStretchLastSection(False)
        # self.listTreeHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.listTreeHeader.setSectionsClickable(True)
        self.listTreeHeader.sectionClicked.connect(self.custom_sort_by_column)

        self.runningWidget.setLayout(running_layout)

        self.finishedWidget = QWidget()
        finished_layout = QGridLayout()

        self.finishedTasksTree = QTreeWidget()
        self.finishedTasksTree.setHeaderLabels(["", "Name", "Description", "Priority", "Start", "End", "Documents"])
        self.finishedTasksTree.setFont(QFont('AnyStyle', self.subtitleFontSize))
        self.finishedTasksTree.setMinimumWidth(1256)
        self.finishedTasksTree.setMinimumHeight(550)
        self.finishedTasksTree.setColumnWidth(0, 50)
        self.finishedTasksTree.setColumnWidth(1, 200)
        self.finishedTasksTree.setColumnWidth(2, 480)
        self.finishedTasksTree.setColumnWidth(3, 200)
        self.finishedTasksTree.setColumnWidth(4, 112)
        self.finishedTasksTree.setColumnWidth(5, 112)
        self.finishedTasksTree.setColumnWidth(6, 100)
        self.finishedTasksTree.itemChanged.connect(self.finished_tasks_tree_changed)
        # self.finishedTasksTree.itemClicked.connect(self.finishedTasksTree_itemClicked)
        self.finishedTasksTree.itemPressed.connect(self.finished_tasks_tree_item_clicked)
        self.finishedTasksTree.itemDoubleClicked.connect(self.modify_task_btn_clicked)
        finished_layout.addWidget(self.finishedTasksTree, 2, 0, 1, 4)

        self.finishedTasksTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.finishedTasksTree.customContextMenuRequested.connect(self.show_lists_context_menu)

        self.finishedTasksTreeHeader = self.finishedTasksTree.header()
        self.finishedTasksTreeHeader.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.finishedTasksTreeHeader.setStretchLastSection(False)
        self.finishedTasksTreeHeader.setSectionsClickable(True)
        self.finishedTasksTreeHeader.sectionClicked.connect(self.custom_sort_by_column)

        self.finishedWidget.setLayout(finished_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.runningWidget, "Running")
        self.tabs.addTab(self.finishedWidget, "Finished")

        layout.addWidget(self.tabs, 1, 1, 2, 1)

        self.web_view = QWebEngineView()
        self.web_view.setFixedHeight(0)
        self.web_view.setVisible(False)
        layout.addWidget(self.web_view, 3, 1)

        if self.config["gantt"]:
            self.web_view.setFixedHeight(250)
            self.web_view.setVisible(True)
            self.web_view.setHtml('''
<html>
<head>
    <style>
        body{
            background-color: black;
            color: white;
        }
    </style>
</head>
<body>
</body>
</html>
''')

        main_window = QWidget()
        main_window.setLayout(layout)  # running_layout
        self.setCentralWidget(main_window)
        # self.setLayout(running_layout)

        self.update_changes()
        self.update_tree()

        self.waitForNotifications = 1800000  # msec  30min = 30*60*1000 = 1.800.000

        self.notifyTimer = QTimer(self)
        self.notifyTimer.timeout.connect(self.notify_user)

        self.showMaximized()

        if self.os == 'linux':
            # --- center window ---
            # - on primary screen -
            # self.move(QGuiApplication.primaryScreen().availableGeometry().center() - self.frameGeometry().center())
            # - on screen where mouse pointer is -
            self.move(QGuiApplication.screenAt(
                QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())
            # ---------------------

        if self.config["notif"]:
            self.notifyTimer.start(self.waitForNotifications)
            self.compute_notification_period()
            self.notify_user()

    def keyPressEvent(self, e):
        pass
        # if e.key() == 16777223:
        #     self.DeleteTaskBtnClicked()

    def update_tree(self):

        self.model.clear()

        def add_item(parent, data):
            item = QStandardItem(data['Name'])
            item.setData(data)
            item.setEditable(False)
            parent.appendRow(item)
            if 'Children' in data:
                for child_ in data['Children']:
                    # add_item(item, child)
                    # if not 'Description' in child:
                    if 'Children' in child_ or 'Description' not in child_:
                        add_item(item, child_)

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
                if 'Name' in child and 'Description' not in child:
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

        self.update_icons()

    def update_icons(self):
        items = []
        root = self.model.invisibleRootItem()
        for item in self.iter_items(root):
            item.setIcon(QIcon())
            items.append(item)

            parent_list = self.generate_parent_list(item)

            parent_name = self.task_tree['Name']
            parent_ = self.task_tree
            tasks_list = None

            if parent_name == parent_list[len(parent_list) - 1]:
                for i in range(len(parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element
                                if "Children" in child:
                                    for eventual_tasks_list in child["Children"]:
                                        if "Check" in eventual_tasks_list:
                                            tasks_list = child["Children"]
                                            # break
                                break

            every_tasks_finished = True
            running_tasks = 0

            if tasks_list is not None:
                for task in tasks_list:
                    if "Children" in task:
                        for subtask in task["Children"]:
                            if "Check" in subtask:
                                if subtask["Check"] == 0:
                                    every_tasks_finished = False
                                    break
                    elif task['Check'] == 0:  # at least one task is not finished
                        every_tasks_finished = False
                        running_tasks += 1
                        # break

                if every_tasks_finished:
                    item.setIcon(QIcon(self.icons["tick"]))
                else:
                    if running_tasks == 1:
                        item.setIcon(QIcon(self.icons["number_1"]))
                    elif running_tasks == 2:
                        item.setIcon(QIcon(self.icons["number_2"]))
                    elif running_tasks == 3:
                        item.setIcon(QIcon(self.icons["number_3"]))
                    elif running_tasks == 4:
                        item.setIcon(QIcon(self.icons["number_4"]))
                    elif running_tasks == 5:
                        item.setIcon(QIcon(self.icons["number_5"]))
                    elif running_tasks == 6:
                        item.setIcon(QIcon(self.icons["number_6"]))
                    elif running_tasks == 7:
                        item.setIcon(QIcon(self.icons["number_7"]))
                    elif running_tasks == 8:
                        item.setIcon(QIcon(self.icons["number_8"]))
                    elif running_tasks == 9:
                        item.setIcon(QIcon(self.icons["number_9"]))
                    elif running_tasks == 10:
                        item.setIcon(QIcon(self.icons["number_10"]))
                    elif running_tasks == 11:
                        item.setIcon(QIcon(self.icons["number_11"]))
                    elif running_tasks == 12:
                        item.setIcon(QIcon(self.icons["number_12"]))
                    elif running_tasks == 13:
                        item.setIcon(QIcon(self.icons["number_13"]))
                    elif running_tasks == 14:
                        item.setIcon(QIcon(self.icons["number_14"]))
                    elif running_tasks == 15:
                        item.setIcon(QIcon(self.icons["number_15"]))
                    elif running_tasks == 16:
                        item.setIcon(QIcon(self.icons["number_16"]))
                    elif running_tasks == 17:
                        item.setIcon(QIcon(self.icons["number_17"]))
                    elif running_tasks == 18:
                        item.setIcon(QIcon(self.icons["number_18"]))
                    elif running_tasks == 19:
                        item.setIcon(QIcon(self.icons["number_19"]))
                    elif running_tasks == 20:
                        item.setIcon(QIcon(self.icons["number_20"]))
                    else:
                        item.setIcon(QIcon(self.icons["folder"]))

    @staticmethod
    def iter_items(root: QStandardItem | None):
        if root is not None:
            stack = [root]
            while stack:
                parent = stack.pop(0)
                for row in range(parent.rowCount()):
                    for column in range(parent.columnCount()):
                        child = parent.child(row, column)
                        yield child
                        # print("child", child)
                        # print("child.text()", child.text())
                        if child.hasChildren():
                            stack.append(child)

    @staticmethod
    def generate_parent_list(item: QStandardItem | None) -> list[QStandardItem]:
        parent_list = []
        child = item
        while child is not None:
            parent_list.append(child.text())
            child = child.parent()

        return parent_list

    def expand_section_tree(self):
        self.tree_view.expandAll()

    def collapse_section_tree(self):
        self.tree_view.collapseAll()

    def on_project_tree_clicked(self, index):
        item = self.model.itemFromIndex(index)
        self.update_icons()
        item.setIcon(QIcon(self.icons["open_folder"]))

        self.ts = time.time()

        self.parent_list = self.generate_parent_list(item)

        project_text = ""
        for i in range(len(self.parent_list)-1, 0, -1):
            if len(self.parent_list)-1 > i > 0:
                project_text += " → " + self.parent_list[i-1]
            else:
                project_text += self.parent_list[i-1]

        self.selectedProjectLbl.setText(project_text)

        parent_name = self.task_tree['Name']
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

        # print("tasks_list:", tasks_list)

        if tasks_list is not None:
            if 'Children' in tasks_list:
                self.selected_project_tasks_list = tasks_list['Children']
            else:
                self.selected_project_tasks_list = None
        else:
            self.selected_project_tasks_list = None

        self.tasksList = self.selected_project_tasks_list
        self.update_changes()

        self.selectedProject = item

    def update_gantt(self):

        if self.parent_list is not None:
            project_name = self.parent_list[0]

            gantt = f"""
~~~mermaid
gantt
dateFormat  YYYY-MM-DD
title       GANTT for {project_name} project
excludes    weekends
"""

            for task in self.tasksList:
                if task["Check"] == 0:
                    status = "done"
                else:
                    status = "active"
                if task["EndDate"] == "-":
                    if self.config["no_end_date_format"] == "Set to today":
                        end_date = QDateTime.currentDateTime().date().toString(Qt.ISODate)
                    else:
                        end_date = self.config["no_end_date"] + "d"
                else:
                    end_date = task["EndDate"]
                gantt += f"{task['Name']}: {status}, crit, {task['StartDate']}, {end_date}\n"

            gantt += "~~~"

            # print(gantt)

# """
# section A section
# Completed task            :done,    des1, 2014-01-06,2014-01-08
# Active task               :active,  des2, 2014-01-09, 3d
# Future task               :         des3, after des2, 5d
# Future task2              :         des4, after des3, 5d
#
# section Critical tasks
# Completed task in the critical line :crit, done, 2014-01-06,24h
# Implement parser and jison          :crit, done, after des1, 2d
# Create tests for parser             :crit, active, 3d
# Future task in critical line        :crit, 5d
# Create tests for renderer           :2d
# Add to mermaid                      :1d
# Functionality added                 :milestone, 2014-01-25, 0d
#
# section Documentation
# Describe gantt syntax               :active, a1, after des1, 3d
# Add gantt diagram to demo page      :after a1  , 20h
# Add another diagram to demo page    :doc1, after a1  , 48h
#
# section Last section
# Describe gantt syntax               :after doc1, 3d
# Add gantt diagram to demo page      :20h
# Add another diagram to demo page    :48h
# ~~~
# """

            gantt_html = markdown.markdown(gantt, extensions=['lib.md_mermaid'])
            self.web_view.setHtml(gantt_html)

    def show_tree_context_menu(self, position):

        if time.time() - self.ts < 0.3:

            add_task = QAction("Add task")
            add_task.triggered.connect(self.add_task_btn_clicked)
            add_section = QAction("Add section")
            add_section.triggered.connect(self.add_subsection_btn_clicked)
            modify_section = QAction("Modify")
            modify_section.triggered.connect(self.modify_section_btn_clicked)
            delete_section = QAction("Delete")
            delete_section.triggered.connect(self.remove_section_btn_clicked)

            menu = QMenu(self.tree_view)
            menu.addAction(add_task)
            menu.addAction(add_section)
            menu.addAction(modify_section)
            menu.addAction(delete_section)

        else:
            add_project = QAction("Add project")
            add_project.triggered.connect(self.add_section_btn_clicked)

            menu = QMenu(self.tree_view)
            menu.addAction(add_project)

        menu.exec(self.tree_view.mapToGlobal(position))

    def open_param_btn_clicked(self):
        self.param_dialog.show()

    def add_section_btn_clicked(self):
        add_project_dialog = QInputDialog(self)
        add_project_dialog.setInputMode(QInputDialog.TextInput)
        add_project_dialog.setWindowTitle('Create new section')
        add_project_dialog.setLabelText('Section name:')
        add_project_dialog.setFont(QFont('AnyStyle', 9))
        ok = add_project_dialog.exec()
        text = add_project_dialog.textValue()

        if ok:
            self.task_tree["Children"].append({"Name": text})

        self.save_tree()
        self.update_tree()

    def add_subsection_btn_clicked(self):

        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element
                                add_section_dialog = QInputDialog(self)
                                add_section_dialog.setInputMode(QInputDialog.TextInput)
                                add_section_dialog.setWindowTitle('Create sub-section')
                                add_section_dialog.setLabelText('Sub-section name:')
                                add_section_dialog.setFont(QFont('AnyStyle', 9))
                                ok = add_section_dialog.exec()
                                text = add_section_dialog.textValue()

                                if ok:
                                    if 'Children' in child:
                                        child['Children'].append({"Name": text})
                                    else:
                                        child['Children'] = []
                                        child['Children'].append({"Name": text})

                                self.save_tree()
                                self.update_tree()
                                self.update_changes()

    def modify_section_btn_clicked(self):
        if self.parent_list is not None:
            parent_name = self.task_tree['Name']
            parent_ = self.task_tree

            if parent_name == self.parent_list[len(self.parent_list) - 1]:
                for i in range(len(self.parent_list), 0, -1):
                    for child in parent_["Children"]:
                        if child['Name'] == self.parent_list[i - 1]:
                            parent_ = child
                            if (i - 1) == 0:  # last element
                                modify_section_dialog = QInputDialog(self)
                                modify_section_dialog.setInputMode(QInputDialog.TextInput)
                                modify_section_dialog.setWindowTitle('Modify section')
                                modify_section_dialog.setLabelText('New section name:')
                                line_edit = modify_section_dialog.findChild(QLineEdit)
                                line_edit.setPlaceholderText(f'{child["Name"]}')
                                modify_section_dialog.setFont(QFont('AnyStyle', 9))
                                ok = modify_section_dialog.exec()
                                text = modify_section_dialog.textValue()

                                if ok:
                                    child['Name'] = text

                                self.save_tree()
                                self.update_tree()
                                self.update_changes()

    def remove_section_btn_clicked(self):
        button = QMessageBox.warning(self,
                                     "Removing section",
                                     f'Section "{self.selectedProject.text()}" is going to be removed,\n'
                                     f'as well as all other potential subsections\n'
                                     f'and tasks that belongs to them.',
                                     buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                     defaultButton=QMessageBox.Ok)

        if button == QMessageBox.Ok:
            if self.parent_list is not None:
                parent_name = self.task_tree['Name']
                parent_ = self.task_tree

                if parent_name == self.parent_list[len(self.parent_list) - 1]:
                    for i in range(len(self.parent_list), 0, -1):
                        for child in parent_["Children"]:
                            if child['Name'] == self.parent_list[i - 1]:

                                if (i - 1) == 0:  # last element

                                    parent_["Children"].remove(child)

                                    self.save_tree()
                                    self.update_tree()
                                    self.update_changes()

                                parent_ = child

    def remove_task(self, task_to_delete):

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
                                    child['Children'].remove(task_to_delete)

                                    self.save_tree()
                                    self.update_tree()
                                    self.update_changes()

    def save_tree(self):
        with open(f'{self.d}{self.slash}tasks_tree.yaml', 'w') as f:
            yaml.dump(self.task_tree, f, sort_keys=False)

    def create_task(self, task):

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

                                self.save_tree()
                                self.update_tree()
                                self.update_changes()

    def update_changes(self):
        self.updating = True

        time.sleep(0.1)

        self.listTree.clearFocus()
        self.finishedTasksTree.clearFocus()
        self.listTree.clearSelection()
        self.finishedTasksTree.clearSelection()
        self.listTree.clear()
        self.finishedTasksTree.clear()
        i_running = 0
        i_finished = 0
        running_tasks_nb = 0
        finished_tasks_nb = 0
        tree_to_build = None

        if self.tasksList is not None:
            new_tasks_list = []
            for task in self.tasksList:
                if "Children" not in task and "Description" in task:
                    new_tasks_list.append(task)
            self.tasksList = new_tasks_list

            for task in self.tasksList:
                if "Check" in task:
                    if task["Check"] == 0:
                        running_tasks_nb += 1
                    elif task["Check"] == 1:
                        finished_tasks_nb += 1
                else:
                    self.tasksList = None
                    break

        if self.tasksList is not None:
            for task in self.tasksList:
                if task["Check"] == 0:
                    tree_to_build = self.listTree
                    i_running += 1
                elif task["Check"] == 1:
                    tree_to_build = self.finishedTasksTree
                    i_finished += 1

                element = QTreeWidgetItem(tree_to_build)
                element.setFlags(element.flags() | Qt.ItemIsUserCheckable)

                lbl = QLabel(f'\n{task["Name"]}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 1, lbl)

                lbl = QLabel(f'\n{task["Description"]}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setMaximumWidth(500)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 2, lbl)

                lbl = QLabel(task["Priority"])
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 3, lbl)

                try:
                    year, month, day = task["StartDate"].split("-")
                    date = f'{day}/{month}/{year}'
                except ValueError:
                    print("ValueError")
                    date = task["StartDate"]

                lbl = QLabel(date)
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 4, lbl)

                try:
                    year, month, day = task["EndDate"].split("-")
                    date = f'{day}/{month}/{year}'
                except ValueError:
                    date = task["EndDate"]

                lbl = QLabel(date)
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 5, lbl)

                if "Documents" in task:

                    widget = QWidget()
                    layout = QGridLayout()
                    widget.setLayout(layout)

                    doc_list = task['Documents']

                    col = 0
                    row = 0
                    max_col = 4

                    for document in doc_list:
                        split_document_path = document.split(".")
                        extension = split_document_path[len(split_document_path)-1]
                        icon = select_icon(self.d, self.slash, extension)

                        split_document_path = document.split(" ")
                        no_space_path = ""

                        for i in range(len(split_document_path)):
                            if len(split_document_path) > i > 0:
                                no_space_path += "\space" + split_document_path[i]
                            else:
                                no_space_path += split_document_path[i]

                        if not os.path.exists(document):
                            icon = self.d + self.slash + "icon" + self.slash + "document-broken.png"

                        path = f"<a href={no_space_path}><img src={icon}></a>"

                        lbl = QLabel(path)
                        lbl.setWordWrap(True)
                        lbl.setFont(QFont('AnyStyle', self.itemFontSize))
                        lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        lbl.linkActivated.connect(self.link_activated)
                        lbl.setToolTip(document)

                        if col < max_col:
                            layout.addWidget(lbl, row, col)
                        else:
                            row += 1
                            col = 0
                            layout.addWidget(lbl, row, col)

                        col += 1

                    tree_to_build.setItemWidget(element, 6, widget)

                if task["Check"] == 1:
                    element.setCheckState(0, Qt.Checked)
                else:
                    element.setCheckState(0, Qt.Unchecked)

        if self.config["gantt"]:
            self.update_gantt()

        self.updating = False

    def link_activated(self, path):
        split_document_path = path.split("\space")
        reconstructed_path = ""

        for i in range(len(split_document_path)):
            if len(split_document_path) > i > 0:
                reconstructed_path += " " + split_document_path[i]
            else:
                reconstructed_path += split_document_path[i]

        if os.path.exists(reconstructed_path):
            folder_path = os.path.dirname(reconstructed_path)

            # on linux only (maybe it works on windows?). If not, use os.startfile(folder_path):
            if self.os == 'linux':
                subprocess.call(["xdg-open", folder_path])
                # subprocess.call(["xdg-open", path])  # to directly open file
            else:
                os.startfile(folder_path)
        else:
            QMessageBox.critical(self,
                                 "File not found",
                                 "The file you are requesting does not exist",
                                 buttons=QMessageBox.Ok,
                                 defaultButton=QMessageBox.Ok)

    def finished_tasks_tree_changed(self, item, col):
        try:
            if not self.updating:

                # if item.checkState(0) == Qt.Checked:
                #     for task in self.tasksList:
                #         if task["Name"] == self.finishedTasksTree.itemWidget(item, 1).text() and \
                #                 task["Description"] == self.finishedTasksTree.itemWidget(item, 2).text():
                #             task["Check"] = 1
                #             break

                if item.checkState(0) == Qt.Unchecked:
                    # breakpoint()
                    for task in self.tasksList:
                        if f'\n{task["Name"]}\n' == self.finishedTasksTree.itemWidget(item, 1).text() and \
                                f'\n{task["Description"]}\n' == self.finishedTasksTree.itemWidget(item, 2).text():
                            # if task["Name"] == self.finishedTasksTree.itemWidget(item, 1).text() and \
                            #         task["Description"] == self.finishedTasksTree.itemWidget(item, 2).text():
                            task["Check"] = 0
                            break

                    self.save_tree()
                    self.update_tree()
                    self.update_changes()
        except Exception as e:
            print("finishedTasksTree_changed:", e)

    def list_tree_changed(self, item, col):
        try:
            if not self.updating:
                if item.checkState(0) == Qt.Checked:
                    # breakpoint()
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

                    self.save_tree()
                    self.update_tree()
                    self.update_changes()
        except Exception as e:
            print("listTree_changed:", e)

    def list_tree_item_clicked(self, item, col):
        try:
            if item.isSelected():
                self.selectedItem = item
                self.ts = time.time()
        except Exception as e:
            print("listTree_itemClicked", e)

    def finished_tasks_tree_item_clicked(self, item, col):
        try:
            if item.isSelected():
                self.selectedItem = item
                self.ts = time.time()
        except Exception as e:
            print("finishedTasksTree_itemClicked", e)

    def add_task_btn_clicked(self):
        # self.Update_project_combo_box()
        self.addTaskDialog.show()

    def modify_task_btn_clicked(self):
        # self.Update_project_combo_box()

        current_tree = self.selected_tree()

        task_to_modify = self.get_task(current_tree)

        self.addTaskDialog.modify_task(task_to_modify)

        # for task in self.tasksList:
        #     if f'\n{task["Name"]}\n' == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #             f'\n{task["Description"]}\n' == current_tree.itemWidget(self.selectedItem, 2).text():
        #     # if task["Name"] == current_tree.itemWidget(self.selectedItem, 1).text() and \
        #     #         task["Description"] == current_tree.itemWidget(self.selectedItem, 2).text():
        #         self.modify_task.emit(task)
        #         break

    def update_task(self, modified_task):

        current_tree = self.selected_tree()

        task = self.get_task(current_tree)

        task["Name"] = modified_task["Name"]
        task["Description"] = modified_task["Description"]
        # task["Project"] = modifiedTask["Project"]
        task["Priority"] = modified_task["Priority"]
        task["StartDate"] = modified_task["StartDate"]
        task["EndDate"] = modified_task["EndDate"]

        task["Documents"] = modified_task["Documents"]

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

        self.save_tree()
        self.update_tree()
        self.update_changes()

    def delete_task_btn_clicked(self):

        current_tree = self.selected_tree()

        task_widget = current_tree.itemWidget(self.selectedItem, 1)
        if task_widget is not None:
            task_name = task_widget.text()
            task_name = task_name.replace("\n", "")

            button = QMessageBox.warning(self,
                                         "Removing task",
                                         f'Task "{task_name}" is going to be removed',
                                         buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                         defaultButton=QMessageBox.Ok)

            if button == QMessageBox.Ok:
                self.on_delete_msg_box_btn_clicked()

        else:
            QMessageBox.warning(self,
                                "Removing task",
                                "No task selected",
                                buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)

    def on_delete_msg_box_btn_clicked(self):
        current_tree = self.selected_tree()
        task_to_delete = self.get_task(current_tree)
        self.tasksList.remove(task_to_delete)
        self.remove_task(task_to_delete)

    def get_task(self, tree):
        for task in self.tasksList:
            if f'\n{task["Name"]}\n' == tree.itemWidget(self.selectedItem, 1).text() and \
                    f'\n{task["Description"]}\n' == tree.itemWidget(self.selectedItem, 2).text():
                # if task["Name"] == tree.itemWidget(self.selectedItem, 1).text() and \
                #         task["Description"] == tree.itemWidget(self.selectedItem, 2).text():
                return task

    def custom_sort_by_column(self, column):
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

        self.update_changes()

    def selected_tree(self):
        if self.tabs.currentWidget() == self.runningWidget:
            return self.listTree
        elif self.tabs.currentWidget() == self.finishedWidget:
            return self.finishedTasksTree

    def show_lists_context_menu(self, position):

        if time.time() - self.ts < 0.1:
            copy_action = QAction("Copy task")
            copy_action.triggered.connect(self.copy_task_btn_clicked)
            cut_action = QAction("Cut task")
            cut_action.triggered.connect(self.cut_task_btn_clicked)
            paste_action = QAction("Paste task here")
            paste_action.triggered.connect(self.paste_task_btn_clicked)
            add_task = QAction("Add task")
            add_task.triggered.connect(self.add_task_btn_clicked)
            modify_action = QAction("Modify task")
            modify_action.triggered.connect(self.modify_task_btn_clicked)
            delete_action = QAction("Delete task")
            delete_action.triggered.connect(self.delete_task_btn_clicked)

            menu = QMenu(self.listTree)
            menu.addAction(copy_action)
            menu.addAction(cut_action)
            menu.addAction(paste_action)
            menu.addAction(add_task)
            menu.addAction(modify_action)
            menu.addAction(delete_action)
        else:
            add_task = QAction("Add task")
            add_task.triggered.connect(self.add_task_btn_clicked)
            paste_action = QAction("Paste task here")
            paste_action.triggered.connect(self.paste_task_btn_clicked)

            menu = QMenu(self.listTree)
            menu.addAction(add_task)
            menu.addAction(paste_action)

        menu.exec(self.listTree.mapToGlobal(position))

    def copy_task_btn_clicked(self):
        current_tree = self.selected_tree()
        task_to_copy = self.get_task(current_tree)

        self.copied_task = {"Name": task_to_copy["Name"] + ' (copy)',
                            "Description": task_to_copy["Description"],
                            "Priority": task_to_copy["Priority"],
                            "StartDate": task_to_copy["StartDate"],
                            "EndDate": task_to_copy["EndDate"],
                            "Check": task_to_copy["Check"],
                            "Documents": task_to_copy["Documents"]}

    def cut_task_btn_clicked(self):
        current_tree = self.selected_tree()
        task_to_cut = self.get_task(current_tree)

        self.copied_task = {"Name": task_to_cut["Name"],
                            "Description": task_to_cut["Description"],
                            "Priority": task_to_cut["Priority"],
                            "StartDate": task_to_cut["StartDate"],
                            "EndDate": task_to_cut["EndDate"],
                            "Check": task_to_cut["Check"],
                            "Documents": task_to_cut["Documents"]}

        button = QMessageBox.warning(self,
                                     "Removing task",
                                     f'Task "{task_to_cut["Name"]}" is going to be cut',
                                     buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                     defaultButton=QMessageBox.Ok)

        if button == QMessageBox.Ok:
            self.on_delete_msg_box_btn_clicked()

    def paste_task_btn_clicked(self):
        if "Name" in self.copied_task:
            self.create_task(self.copied_task)
        else:
            QMessageBox.warning(self,
                                "No task copied",
                                "No task to paste",
                                buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)

    def update_config(self):
        if self.config["notif"]:
            self.compute_notification_period()

        if self.config["gantt"] and not self.web_view.isVisible():
            self.web_view.setFixedHeight(250)
            self.web_view.setVisible(True)
            # self.listTree.setMinimumHeight(550)
            # self.finishedTasksTree.setMinimumHeight(550)
            self.setGeometry(self.pos().x(), self.pos().y()-250/2, self.width(), self.height())
        elif not self.config["gantt"] and self.web_view.isVisible():
            self.web_view.setFixedHeight(0)
            self.web_view.setVisible(False)
            self.setGeometry(self.pos().x(), self.pos().y(), self.width(), self.height()-250)

        self.update_changes()

    def compute_notification_period(self):

        self.notifyTimer.stop()

        if self.config["notif"]:
            time_factor = 24*3600*1000
            if self.config["unit"] == "minutes":
                time_factor = 60*1000
            elif self.config["unit"] == "hours":
                time_factor = 3600*1000

            self.waitForNotifications = int(self.config["period"])*time_factor

            self.notifyTimer.start(self.waitForNotifications)

    def notify_user(self):

        today = QDate.currentDate()

        date = QDate()
        date.setDate(QDate.year(today), QDate.month(today), QDate.day(today))
        day_number = date.dayOfWeek()

        end_of_week = today.addDays(7-day_number)

        today_day, today_month, today_year = today.toString(Qt.ISODate).split("-")
        today_str = today_day + today_month + today_year
        end_of_week_day, end_of_week_month, end_of_week_year = end_of_week.toString(Qt.ISODate).split("-")
        end_of_week_str = end_of_week_day + end_of_week_month + end_of_week_year

        passed_list = ["TASKS FOR WHICH THE DEADLINE HAS PASSED:"]

        today_list = ["Here are the tasks for today:"]

        end_of_week_list = ["This week's tasks include:"]

        if self.tasksList is not None:
            for task in self.tasksList:
                if task["Check"] == 0:
                    try:
                        task_end_date_day, task_end_date_month, task_end_date_year = task["EndDate"].split("-")
                        task_end_date = task_end_date_day + task_end_date_month + task_end_date_year

                        if task_end_date < today_str:
                            passed_list.append(f' - {task["Name"]}')
                        elif task_end_date == today_str:
                            today_list.append(f' - {task["Name"]}')
                        elif task_end_date <= end_of_week_str:
                            end_of_week_list.append(f' - {task["Name"]}')
                    except ValueError:
                        pass  # no end date

        notification_text = ""

        if len(passed_list) > 1:
            for line in passed_list:
                notification_text += ("\n" + line)
            notification_text += "\n"

        if len(today_list) > 1:
            for line in today_list:
                notification_text += ("\n" + line)
            notification_text += "\n"

        if len(end_of_week_list) > 1:
            for line in end_of_week_list:
                notification_text += ("\n" + line)

        if len(passed_list) == 1 and len(today_list) == 1 and len(end_of_week_list) == 1:
            notification_text = "You are up to date for this week"

        self.notifyTimer.stop()

        QMessageBox.information(self,
                                "Your tasks",
                                notification_text,
                                buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)

        self.notifyTimer.start(self.waitForNotifications)


if __name__ == "__main__":
    app = QApplication([])

    style(app)

    mainWindow = MainWindow()
    sys.exit(app.exec())
