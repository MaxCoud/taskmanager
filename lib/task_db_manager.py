import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, Signal, QDateTime, QDate
from PySide6.QtGui import QStandardItemModel, QFont, Qt, QGuiApplication, QCursor, QCloseEvent, QStandardItem, QIcon, \
    QTextOption, QMouseEvent, QAction
from PySide6.QtWidgets import QGridLayout, QWidget, QMainWindow, QTreeView, QLabel, QTreeWidget, QTabWidget, \
    QApplication, QLineEdit, QPlainTextEdit, QTreeWidgetItem, QDateEdit, QHBoxLayout, QCheckBox, QComboBox, QPushButton, \
    QMenu, QMessageBox, QFileDialog
from peewee import *
import time
from lib.style import style, select_icon, load_icons

from PySide6.QtCore import QObject


class TestWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.os = sys.platform

        # change working directory to this script directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.d = os.getcwd()

        # linux shortcut
        if self.os == 'linux':
            self.slash = "/"

        elif self.os == 'windows' or self.os == 'win32':
            self.slash = "\\"

        self.setWindowTitle("Task Manager")

        self.tasksList = None
        self.projectList = []
        self.selected_item = None
        self.selected_task = None
        self.selected_section = None
        self.parent_list = None
        self.selectedProject = None
        self.selected_project_tasks_list = None
        self.updating = False
        self.copied_task = {}
        self.last_dir = "/"
        self.modifying = False
        self.start_app = True

        # self.projectAscending = None
        self.priorityAscending = None
        self.startDateAscending = None
        self.endDateAscending = None
        self.ts = time.time()  # store timestamp

        self.icons = load_icons(Path(__file__).resolve().parent.parent)

        database_path = f'{Path(__file__).resolve().parent}{self.slash}task_database.db'
        self.task_database_manager = TaskDatabaseManager(database_path)

        self.setWindowModality(Qt.ApplicationModal)

        self.title_font_size = 14
        self.subtitle_font_size = 11
        self.item_font_size = 10

        layout = QGridLayout()

        self.runningWidget = QWidget()
        running_layout = QGridLayout()

        self.tree_view = CustomTreeView()
        self.tree_view.setFixedWidth(300)
        # self.tree_view.clicked.connect(self.on_project_tree_clicked)
        self.tree_view.pressed.connect(self.on_project_tree_clicked)
        layout.addWidget(self.tree_view, 0, 0, 4, 1)

        self.tree_view.clicked_outside.connect(self.mousePressEvent)

        # create a model for tree view
        self.model = QStandardItemModel()

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_tree_context_menu)

        # get header of tree view
        self.tree_view_header = self.tree_view.header()
        # self.tree_view_header.setSectionResizeMode(QHeaderView.Interactive)

        self.selectedProjectLbl = QLabel()
        self.selectedProjectLbl.setText("No project selected")
        self.selectedProjectLbl.setFont(QFont('AnyStyle', self.title_font_size))
        self.selectedProjectLbl.setFixedHeight(30)
        self.selectedProjectLbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selectedProjectLbl, 0, 1, 1, 2)

        self.list_tree = CustomTreeWidget()
        self.list_tree.setHeaderLabels(["Name", "Description"])
        self.list_tree.setFont(QFont('AnyStyle', self.subtitle_font_size))
        self.list_tree.setMinimumWidth(750)
        self.list_tree.setMinimumHeight(100)
        self.list_tree.setColumnWidth(0, 300)
        # self.listTree.setColumnWidth(1, 680)

        self.list_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_tree.customContextMenuRequested.connect(self.show_lists_context_menu)

        self.list_tree.itemChanged.connect(self.list_tree_changed)
        # self.listTree.itemClicked.connect(self.listTree_itemClicked)
        self.list_tree.itemPressed.connect(self.item_clicked)
        self.list_tree.itemDoubleClicked.connect(self.modify_task_btn_clicked)
        self.list_tree.clicked_outside.connect(self.mousePressEvent)
        running_layout.addWidget(self.list_tree, 0, 0)

        self.list_tree_header = self.list_tree.header()
        self.list_tree_header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.list_tree_header.setStretchLastSection(True)
        self.list_tree_header.setSectionsClickable(True)
        self.list_tree_header.sectionClicked.connect(self.custom_sort_by_column)

        self.finishedWidget = QWidget()
        finished_layout = QGridLayout()

        self.finished_tree = CustomTreeWidget()
        self.finished_tree.setHeaderLabels(["Name", "Description"])
        self.finished_tree.setFont(QFont('AnyStyle', self.subtitle_font_size))
        self.finished_tree.setMinimumWidth(750)
        self.finished_tree.setMinimumHeight(500)
        self.finished_tree.setColumnWidth(0, 300)
        # self.finishedTasksTree.setColumnWidth(1, 680)
        self.finished_tree.itemChanged.connect(self.finished_tasks_tree_changed)
        # self.finishedTasksTree.itemClicked.connect(self.finishedTasksTree_itemClicked)
        self.finished_tree.itemPressed.connect(self.item_clicked)
        self.finished_tree.itemDoubleClicked.connect(self.modify_task_btn_clicked)
        self.finished_tree.clicked_outside.connect(self.mousePressEvent)
        finished_layout.addWidget(self.finished_tree, 0, 0)

        self.finished_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.finished_tree.customContextMenuRequested.connect(self.show_lists_context_menu)

        self.finished_tree_header = self.finished_tree.header()
        self.finished_tree_header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.finished_tree_header.setStretchLastSection(True)
        self.finished_tree_header.setSectionsClickable(True)
        self.finished_tree_header.sectionClicked.connect(self.custom_sort_by_column)

        self.finishedWidget.setLayout(finished_layout)

        # --- item details ---
        item_details_grid = QGridLayout()

        lbl = QLabel("Item details")
        # lbl.setFixedWidth(250)
        lbl.setFont(QFont('AnyStyle', self.title_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 0, 0, 1, 3)

        self.name_line_edit = QLineEdit()
        # self.name_line_edit.setFixedWidth(350)
        self.name_line_edit.setFixedHeight(40)
        self.name_line_edit.setFont(QFont('AnyStyle', self.subtitle_font_size))
        self.name_line_edit.textChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.name_line_edit, 1, 0, 1, 3)

        self.description_text_edit = QPlainTextEdit()
        # self.description_text_edit.setFixedWidth(350)
        self.description_text_edit.setMinimumHeight(110)
        self.description_text_edit.setWordWrapMode(QTextOption.WordWrap.WrapAtWordBoundaryOrAnywhere)
        self.description_text_edit.setFont(QFont('AnyStyle', self.item_font_size))
        self.description_text_edit.textChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.description_text_edit, 2, 0, 1, 3)

        lbl = QLabel("Progress")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 3, 0)

        self.progress_line_edit = QLineEdit()
        # self.progress_line_edit.setFixedWidth(180)
        self.progress_line_edit.setFixedHeight(40)
        self.progress_line_edit.setFont(QFont('AnyStyle', self.item_font_size))
        self.progress_line_edit.textChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.progress_line_edit, 3, 1)

        lbl = QLabel("%")
        lbl.setFixedWidth(40)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 3, 2)

        lbl = QLabel("Start Date")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 4, 0)

        self.start_date_edit = QDateEdit(calendarPopup=True)
        # self.start_date_edit.setMinimumWidth(240)
        self.start_date_edit.setFixedHeight(40)
        self.start_date_edit.setFont(QFont('AnyStyle', self.item_font_size))
        self.start_date_edit.userDateChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.start_date_edit, 4, 1, 1, 2)

        lbl = QLabel("End date")
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 5, 0)

        end_date_layout = QHBoxLayout()

        self.end_date_checkbox = QCheckBox()
        self.end_date_checkbox.stateChanged.connect(self.end_date_checkbox_state_changed)

        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setEnabled(False)
        # self.end_date_edit.setMinimumWidth(220)
        self.end_date_edit.setFixedHeight(40)
        self.end_date_edit.userDateChanged.connect(self.modification_detected)
        self.end_date_edit.setFont(QFont('AnyStyle', self.item_font_size))

        end_date_layout.addWidget(self.end_date_checkbox, 0)
        end_date_layout.addWidget(self.end_date_edit, 1)

        item_details_grid.addLayout(end_date_layout, 5, 1, 1, 2)

        lbl = QLabel("Priority")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 6, 0)

        self.priority_combobox = QComboBox()
        # self.priority_combobox.setMinimumWidth(240)
        self.priority_combobox.setFixedHeight(40)
        self.priority_combobox.currentTextChanged.connect(self.modification_detected)
        self.priority_combobox.setFont(QFont('AnyStyle', self.item_font_size))
        item_details_grid.addWidget(self.priority_combobox, 6, 1, 1, 2)

        for i in range(0, len(self.task_database_manager.priority_degrees)):
            self.priority_combobox.insertItem(i, str(self.task_database_manager.priority_degrees[i]))

        lbl = QLabel("Milestone")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 7, 0)

        self.milestone_checkbox = QCheckBox()
        self.milestone_checkbox.stateChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.milestone_checkbox, 7, 1)

        lbl = QLabel("Precedents")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 8, 0)

        self.precedents_combobox = QComboBox()
        # self.precedents_combobox.setMinimumWidth(200)
        self.precedents_combobox.setFixedHeight(40)
        self.precedents_combobox.setFont(QFont('AnyStyle', self.item_font_size))
        self.precedents_combobox.currentTextChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.precedents_combobox, 8, 1)

        self.precedents_combobox_refs = []

        self.set_precedents_btn = QPushButton("...")
        self.set_precedents_btn.setFixedWidth(40)
        self.set_precedents_btn.setFixedHeight(40)
        self.set_precedents_btn.setFont(QFont('AnyStyle', self.item_font_size))
        self.set_precedents_btn.clicked.connect(self.on_set_precedents_btn)
        item_details_grid.addWidget(self.set_precedents_btn, 8, 2)

        lbl = QLabel("Sub tasks")
        # lbl.setFixedWidth(80)
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 9, 0)

        self.subtasks_combobox = QComboBox()
        # self.subtasks_combobox.setMinimumWidth(240)
        self.subtasks_combobox.setFixedHeight(40)
        self.subtasks_combobox.setFont(QFont('AnyStyle', self.item_font_size))
        self.subtasks_combobox.currentTextChanged.connect(self.modification_detected)
        item_details_grid.addWidget(self.subtasks_combobox, 9, 1)

        self.subtasks_combobox_refs = []

        self.set_subtasks_btn = QPushButton("...")
        self.set_subtasks_btn.setFixedWidth(40)
        self.set_subtasks_btn.setFixedHeight(40)
        self.set_subtasks_btn.setFont(QFont('AnyStyle', self.item_font_size))
        self.set_subtasks_btn.clicked.connect(self.on_set_subtasks_btn)
        item_details_grid.addWidget(self.set_subtasks_btn, 9, 2)

        lbl = QLabel("Documents")
        lbl.setFixedHeight(40)
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        item_details_grid.addWidget(lbl, 10, 0)

        browse_layout = QHBoxLayout()

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedHeight(40)
        browse_btn.setFixedWidth(80)
        browse_btn.setFont(QFont('AnyStyle', self.subtitle_font_size))
        browse_btn.clicked.connect(self.browse_btn_clicked)
        browse_layout.addWidget(browse_btn, alignment=Qt.AlignLeft)

        self.files_layout = QGridLayout()
        self.files_layout_row = 0
        self.files_layout_column = 0
        self.files_labels = []
        files_layout_widget = QWidget()
        files_layout_widget.setLayout(self.files_layout)
        browse_layout.addWidget(files_layout_widget, alignment=Qt.AlignLeft)

        item_details_grid.addLayout(browse_layout, 10, 1, 1, 2)
        self.documents_list = []

        save_btn = QPushButton("Save modifications")
        save_btn.setFixedHeight(50)
        save_btn.setFont(QFont('AnyStyle', self.title_font_size))
        save_btn.clicked.connect(self.save_modifications)
        item_details_grid.addWidget(save_btn, 11, 0, 1, 3)

        self.item_details_grid_widget = QWidget()
        self.item_details_grid_widget.setFixedWidth(300)
        # self.item_details_grid_widget.setFixedHeight(500)
        self.item_details_grid_widget.setLayout(item_details_grid)
        self.list_tree.set_details_widget(self.item_details_grid_widget)
        self.finished_tree.set_details_widget(self.item_details_grid_widget)

        # ----
        # ----

        self.runningWidget.setLayout(running_layout)

        self.tabs = QTabWidget()
        # self.tabs.setMinimumHeight(300)
        self.tabs.setFixedHeight(400)
        self.tabs.addTab(self.runningWidget, "Running")
        self.tabs.addTab(self.finishedWidget, "Finished")

        layout.addWidget(self.tabs, 1, 1, 2, 1, Qt.AlignTop)
        layout.addWidget(self.item_details_grid_widget, 1, 2, 2, 1, Qt.AlignTop)

        main_window = QWidget()
        main_window.setLayout(layout)  # running_layout
        self.setCentralWidget(main_window)
        # self.setLayout(running_layout)

        # self.update_changes()
        self.update_tree()

        self.showMaximized()
        # self.item_details_grid_widget.hide()

        # Install event filter on the central widget
        self.item_details_grid_widget.installEventFilter(self)

        if self.os == 'linux':
            # --- center window ---
            # - on primary screen -
            # self.move(QGuiApplication.primaryScreen().availableGeometry().center() - self.frameGeometry().center())
            # - on screen where mouse pointer is -
            self.move(QGuiApplication.screenAt(
                QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())
            # ---------------------

    def mousePressEvent(self, event):
        pos = event.position()
        widget = self.childAt(QPoint(pos.x(), pos.y()))
        if not isinstance(widget, QTreeWidget):
            if self.selected_item is not None:
                if self.selected_item.isSelected():
                    self.list_tree.clearSelection()
                    self.finished_tree.clearSelection()
                    # if self.item_details_grid_widget.isVisible():
                    #     self.item_details_grid_widget.hide()
        super().mousePressEvent(event)

    def modification_detected(self):
        if self.start_app:
            self.start_app = False
        elif not self.modifying:
            self.modifying = True

    def end_date_checkbox_state_changed(self):
        if self.end_date_checkbox.isChecked():
            self.end_date_edit.setEnabled(True)
        else:
            self.end_date_edit.setEnabled(False)

    def on_project_tree_clicked(self, index):
        if self.modifying_msg_box():
            # Get item and set open folder item
            item = self.model.itemFromIndex(index)
            self.update_icons()
            item.setIcon(QIcon(self.icons["open_folder"]))
            # ---------------------------------

            self.ts = time.time()

            # Build selected project title
            self.parent_list = self.generate_parent_list(item)
            project_text = ""
            for i in range(len(self.parent_list) - 1, 0, -1):
                if len(self.parent_list) - 1 > i > 0:
                    project_text += " → " + self.parent_list[i - 1]
                else:
                    project_text += self.parent_list[i - 1]

            self.selectedProjectLbl.setText(project_text)
            # ----------------------------

            self.selected_section = self.task_database_manager.get_task(task_id=item.ref)
            self.update_changes()

    def modifying_msg_box(self):
        if self.modifying:
            button = QMessageBox.warning(self,
                                         "Modifying task",
                                         f"Modifications will be lost, do you want to continue?",
                                         buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                         defaultButton=QMessageBox.Ok)

            if button == QMessageBox.Ok:
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def generate_parent_list(item: QStandardItem | None) -> list[QStandardItem]:
        parent_list = []
        child = item
        while child is not None:
            parent_list.append(child.text())
            child = child.parent()

        return parent_list

    def show_tree_context_menu(self):
        pass

    def list_tree_changed(self):
        pass

    def item_clicked(self, item):
        if self.modifying_msg_box():
            self.selected_item = item
            self.selected_task = self.task_database_manager.get_task(task_id=item.ref)
            self.display_details(self.selected_task)
            self.ts = time.time()

            self.modifying = False

    def display_details(self, task):
        self.name_line_edit.setText(task.name)
        self.description_text_edit.setPlainText(task.description)
        self.progress_line_edit.setText(str(task.progress))

        self.start_date_edit.setDate(task.start_date)
        if task.end_date == "":
            self.end_date_edit.setDate(QDate.currentDate())
            self.end_date_checkbox.setChecked(False)
        else:
            self.end_date_edit.setDate(task.end_date)
            self.end_date_checkbox.setChecked(True)

        self.priority_combobox.setCurrentText(str(task.priority))
        self.milestone_checkbox.setChecked(task.milestone)

        self.precedents_combobox.clear()
        for task_id in task.precedents:
            task_name = self.task_database_manager.get_task(task_id).name
            self.precedents_combobox.addItem(task_name)

        self.subtasks_combobox.clear()
        for task_id in task.subtasks:
            task_name = self.task_database_manager.get_task(task_id).name
            self.subtasks_combobox.addItem(task_name)

        self.documents_list.clear()
        self.display_selected_documents(task.documents)

        # self.item_details_grid_widget.show()

    def finished_tasks_tree_changed(self):
        pass

    def modify_task_btn_clicked(self):
        pass

    def show_lists_context_menu(self):
        pass

    def custom_sort_by_column(self):
        pass

    def update_changes(self):
        """
        Create tasks lists from selected section
        """
        self.list_tree.clear()
        self.finished_tree.clear()

        self.display_details(self.selected_section)

        self.precedents_combobox_refs.clear()

        for subtask_id in self.selected_section.subtasks:
            task = self.task_database_manager.get_task(task_id=subtask_id)

            if len(task.subtasks) == 0:
                if task.progress < 100:
                    tree_to_build = self.list_tree
                else:
                    tree_to_build = self.finished_tree

                element = CustomTreeWidgetItem(ref=task.ref, tree=tree_to_build)

                lbl = QLabel(f'\n{task.name}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.item_font_size))
                lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 0, lbl)

                lbl = QLabel(f'\n{task.description}\n')
                lbl.setWordWrap(True)
                lbl.setFont(QFont('AnyStyle', self.item_font_size))
                # lbl.setMaximumWidth(500)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                tree_to_build.setItemWidget(element, 1, lbl)

            self.precedents_combobox_refs.append(task.ref)
            self.modifying = False

        # ---------------

    def update_tree(self):

        self.model.clear()

        def add_item(parent, data):
            item = CustomStandardItem(ref=data.ref, text=data.name)
            item.setData(data)
            item.setEditable(False)
            parent.appendRow(item)

            for subtask_id in data.subtasks:
                if len(self.task_database_manager.get_task(subtask_id).subtasks) > 0:
                    add_item(item, self.task_database_manager.get_task(subtask_id))

        # create the root item and add it to the model
        root_item = CustomStandardItem(ref=1, text=self.task_database_manager.get_task(task_id=1).name)
        root_item.setData(self.task_database_manager.get_every_task())
        self.model.appendRow(root_item)

        # set label of tree header with root name
        self.model.setHorizontalHeaderLabels(["Projects"])

        if self.task_database_manager.get_task(task_id=1).subtasks == [0]:
            for task in self.task_database_manager.get_every_task():
                print(f'{task=}')
                if len(task.subtasks) > 0:
                    has_parent = False
                    for task_ in self.task_database_manager.get_every_task():
                        if task.ref in task_.subtasks:
                            has_parent = True
                    if not has_parent:
                        add_item(root_item, self.task_database_manager.get_task(task.ref))

        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()

        # hide root element
        self.tree_view.setRootIndex(self.model.index(0, 0))

        self.tree_view_header.resizeSection(0, self.tree_view.sizeHintForColumn(0))

        self.update_icons()

    def update_icons(self):

        # Function to recursively iterate through items and their children
        def iterate_items(item):
            if item.ref != 1:
                subtasks_length = len(self.task_database_manager.get_task(task_id=item.ref).subtasks)
                for subtask_id in self.task_database_manager.get_task(task_id=item.ref).subtasks:
                    if self.task_database_manager.get_task(task_id=subtask_id).progress == 100:
                        subtasks_length -= 1
                if subtasks_length == 0:
                    item.setIcon(QIcon(self.icons["tick"]))
                elif subtasks_length > 20:
                    item.setIcon(QIcon(self.icons["folder"]))
                else:
                    item.setIcon(QIcon(self.icons[subtasks_length]))

            for row in range(item.rowCount()):
                child_item = item.child(row)
                iterate_items(child_item)

        iterate_items(self.model.item(0))

    def browse_btn_clicked(self):
        file = QFileDialog.getOpenFileNames(parent=self,
                                            caption="Select one or more file(s)",
                                            dir=self.last_dir)
        if file:
            if file[0]:
                files_paths = file[0]
                self.last_dir = os.path.dirname(files_paths[0])
                self.display_selected_documents(files_paths)

    def save_modifications(self):
        button = QMessageBox.warning(self,
                                     "Modifying task",
                                     f"Task {self.selected_task.name} will be modified",
                                     buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                     defaultButton=QMessageBox.Ok)

        if button == QMessageBox.Ok:
            self.task_database_manager.set_name(task_id=self.selected_task.ref,
                                                new_name=self.name_line_edit.text())
            self.task_database_manager.set_description(task_id=self.selected_task.ref,
                                                       new_desc=self.description_text_edit.toPlainText())
            self.task_database_manager.set_progress(task_id=self.selected_task.ref,
                                                    new_progress=int(self.progress_line_edit.text()))
            self.task_database_manager.set_start_date(task_id=self.selected_task.ref,
                                                      new_start_date=self.start_date_edit.date().toString(Qt.ISODate))
            if not self.end_date_checkbox.isChecked():
                task_end_date = ""
            else:
                task_end_date = self.end_date_edit.date().toString(Qt.ISODate)
            self.task_database_manager.set_end_date(task_id=self.selected_task.ref,
                                                    new_end_date=task_end_date)

            self.task_database_manager.set_priority(task_id=self.selected_task.ref,
                                                    new_priority=int(self.priority_combobox.currentText()))

            self.task_database_manager.set_milestone(task_id=self.selected_task.ref,
                                                     new_milestone_state=self.milestone_checkbox.isChecked())

            self.task_database_manager.set_documents(task_id=self.selected_task.ref,
                                                     file_paths=self.documents_list)
            self.documents_list.clear()  # need to clear it now

            self.update_changes()

    def display_selected_documents(self, files_paths):

        for file in files_paths:
            if file not in self.documents_list:
                self.documents_list.append(file)

        files_paths = self.documents_list.copy()
        self.documents_list.clear()

        while self.files_layout.count():
            item = self.files_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.files_labels = []
        self.files_layout_column = 0
        self.files_layout_row = 0

        if len(files_paths) > 0:
            for document in files_paths:
                if document != "":
                    split_document_path = document.split(".")
                    extension = split_document_path[len(split_document_path) - 1]

                    if not os.path.exists(document):
                        icon = f'{Path(__file__).resolve().parent.parent}{self.slash}icon{self.slash}document-broken.png'
                    else:
                        icon = select_icon(f'{Path(__file__).resolve().parent.parent}', self.slash, extension)

                    path = f"<a href={document}><img src={icon}></a>"

                    lbl = QLabel(path)
                    lbl.setWordWrap(True)
                    lbl.setFont(QFont('AnyStyle', self.item_font_size))
                    lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    lbl.linkActivated.connect(self.link_activated)
                    lbl.setToolTip(document)
                    self.files_labels.append(lbl)

                    context_menu_fn = self.make_context_menu_fn(lbl)  # create a separate context menu for each label

                    lbl.setContextMenuPolicy(Qt.CustomContextMenu)
                    lbl.customContextMenuRequested.connect(context_menu_fn)

                    if self.files_layout_column < 5:
                        self.files_layout.addWidget(lbl, self.files_layout_row, self.files_layout_column)
                    else:
                        self.files_layout_row += 1
                        self.files_layout_column = 0
                        self.files_layout.addWidget(lbl, self.files_layout_row, self.files_layout_column)

                    self.files_layout_column += 1

                    self.documents_list.append(document)

    def make_context_menu_fn(self, lbl):  # Define a function to create a closure for a label
        context_menu = self.create_document_context_menu(lbl)

        def show_context_menu(pos):
            # context_menu.exec_(lbl.mapToGlobal(pos))
            context_menu.exec(lbl.mapToGlobal(pos))

        return show_context_menu

    def create_document_context_menu(self, lbl):  # Define a function to create the context menu for a QLabel

        context_menu = QMenu()
        delete_selection = QAction("Remove from selection", context_menu)
        context_menu.addAction(delete_selection)

        def remove_label():  # remove the label from its parent
            lbl.setParent(None)
            self.files_labels.remove(lbl)
            self.documents_list.remove(lbl.toolTip())

        delete_selection.triggered.connect(remove_label)
        return context_menu

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

    def on_set_precedents_btn(self):
        pass

    def on_set_subtasks_btn(self):
        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.modifying_msg_box():
            self.task_database_manager.close_db()
        else:
            event.ignore()


class CustomStandardItem(QStandardItem):

    def __init__(self, ref, text=''):
        super().__init__(text)
        self.ref = ref


class CustomTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, ref, tree: QTreeWidget):
        super().__init__(tree)
        self.ref = ref


class CustomTreeView(QTreeView):

    clicked_outside = Signal(QMouseEvent)

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        pos = event.position()
        index = self.indexAt(QPoint(pos.x(), pos.y()))
        if not index.isValid():
            self.clicked_outside.emit(event)
            event.accept()
        super().mousePressEvent(event)


class CustomTreeWidget(QTreeWidget):

    clicked_outside = Signal(QMouseEvent)

    def __init__(self, item_details_widget: QWidget = None):
        super().__init__()
        self.item_details_widget = item_details_widget

    def set_details_widget(self, item_details_widget: QWidget):
        self.item_details_widget = item_details_widget

    def mousePressEvent(self, event):
        pos = event.position()
        item = self.itemAt(QPoint(pos.x(), pos.y()))
        if not item:
            self.clearSelection()
            if self.item_details_widget is not None:
                self.clicked_outside.emit(event)
                event.accept()

                # if self.item_details_widget.isVisible():
                #     self.item_details_widget.hide()
        super().mousePressEvent(event)


# Define a custom field type for storing a list of strings
class ListField(Field):
    def db_value(self, value):
        if value is not None:
            return ','.join(value)

    def python_value(self, value):
        if value is not None:
            return value.split(',')


# Define a custom field type for storing a list of integers
class IntListField(Field):
    def db_value(self, value):
        if value is not None:
            return ','.join(str(x) for x in value)

    def python_value(self, value):
        if value is not None and value != '':
            return [int(x) for x in value.split(',')]
        else:
            return []


class Task(Model):

    # TODO: add levels to access to some tasks and modify them (manager, operator)
    ref = AutoField()  # primary key
    name = CharField()  # task name
    description = CharField()  # task description
    start_date = DateField()  # task start date
    end_date = DateField()  # task end date
    documents = ListField()  # list of documents
    priority = IntegerField()  # task priority
    milestone = BooleanField()  # task is milestone or not
    precedents = IntListField()  # list of tasks that need to be done before this one
    progress = IntegerField()  # task progression, from 0 to 100%
    subtasks = IntListField()  # list of sub-tasks, if any this task became a section

    def __str__(self):
        return f'Task(ref={self.ref}, name={self.name}, description={self.description}, start_date={self.start_date},' \
               f' end_date={self.end_date}, documents={self.documents}, priority={self.priority},' \
               f' milestone={self.milestone}, precedents={self.precedents}, progress={self.progress},' \
               f' subtasks={self.subtasks})'

    class Meta:
        database = None  # SQLite database file


class TaskDatabaseManager(QObject):

    def __init__(self, db_path: str):
        super().__init__()

        self.tasks_db = SqliteDatabase(db_path)

        Task._meta.database = self.tasks_db

        self.tasks_db.connect()

        if not os.path.exists(db_path):
            self.tasks_db.create_tables([Task], safe=True)
            self.add_task(name="Projects", subtasks=[0])

        self.priority_degrees = (1, 2, 3, 4, 5)

    def add_task(self, name="", description="", start_date="", end_date="", documents=None,
                 priority=None, milestone=False, precedents=None, progress=0,
                 subtasks=None) -> Task.ref:
        if subtasks is None:
            subtasks = []
        if precedents is None:
            precedents = []
        if documents is None:
            documents = []
        if priority is None:
            priority = max(self.priority_degrees)

        task = Task(name=name,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    documents=documents,
                    priority=priority,
                    milestone=milestone,
                    precedents=precedents,
                    progress=progress,
                    subtasks=subtasks
                    )
        task.save()
        return task.ref

    @staticmethod
    def set_name(task_id, new_name: str):
        task = Task.get(Task.ref == task_id)
        task.name = new_name
        task.save()

    @staticmethod
    def set_description(task_id, new_desc: str):
        task = Task.get(Task.ref == task_id)
        task.description = new_desc
        task.save()

    @staticmethod
    def add_subtask(parent_id, child_id: int):
        task = Task.get(Task.ref == parent_id)
        if child_id not in task.subtasks:
            task.subtasks.append(child_id)
            task.save()

    @staticmethod
    def remove_subtask(parent_id, child_id: int):
        task = Task.get(Task.ref == parent_id)
        task.subtasks.remove(child_id)
        task.save()

    @staticmethod
    def get_task(task_id: int):
        return Task.get(Task.ref == task_id)

    @staticmethod
    def get_every_task(with_root=False):
        if with_root:
            return Task.select()
        else:
            return Task.select().where(Task.ref != 1)

    @staticmethod
    def remove_task(task_id: int):
        try:
            task_to_remove = Task.get(Task.ref == task_id)
            task_to_remove.delete_instance()
        except Task.DoesNotExist:
            print(f"Task with ref={task_id} does not exists in database")

    @staticmethod
    def set_progress(task_id: int, new_progress: int):
        task = Task.get(Task.ref == task_id)
        task.progress = new_progress
        task.save()

    @staticmethod
    def set_start_date(task_id: int, new_start_date):
        task = Task.get(Task.ref == task_id)
        task.start_date = new_start_date
        task.save()

    @staticmethod
    def set_end_date(task_id, new_end_date):
        task = Task.get(Task.ref == task_id)
        task.end_date = new_end_date
        task.save()

    @staticmethod
    def set_priority(task_id, new_priority):
        task = Task.get(Task.ref == task_id)
        task.priority = new_priority
        task.save()

    @staticmethod
    def set_milestone(task_id, new_milestone_state):
        task = Task.get(Task.ref == task_id)
        task.milestone = new_milestone_state
        task.save()

    @staticmethod
    def add_precedent(task_id, precedent_id):
        task = Task.get(Task.ref == task_id)
        if precedent_id not in task.precedents:
            task.precedents.append(precedent_id)
            task.save()

    @staticmethod
    def remove_precedent(task_id, precedent_id):
        task = Task.get(Task.ref == task_id)
        task.precedents.remove(precedent_id)
        task.save()

    @staticmethod
    def add_document(task_id, file_path):
        task = Task.get(Task.ref == task_id)
        if file_path not in task.documents:
            task.documents.append(file_path)
            task.save()

    @staticmethod
    def remove_document(task_id, file_path):
        task = Task.get(Task.ref == task_id)
        task.documents.remove(file_path)
        task.save()

    @staticmethod
    def set_documents(task_id, file_paths: list[str]):
        task = Task.get(Task.ref == task_id)
        task.documents = file_paths
        task.save()

    def clear_db(self, force=False):
        if force:
            for task in self.get_every_task(with_root=True):
                self.remove_task(task.ref)
        else:
            for task in self.get_every_task():
                self.remove_task(task.ref)

    def close_db(self):
        self.tasks_db.close()


if __name__ == '__main__':

    app = QApplication([])
    mainWindow = TestWindow()
    sys.exit(app.exec())

    # db_path = f'{Path(__file__).resolve().parent}\\task_database.db'
    # task_database_manager = TaskDatabaseManager(db_path)
    #
    # ref = task_database_manager.add_task(name="Task2bis.1", description="desc", start_date="2024-02-29", end_date="2024-02-29",
    #                                      documents=[], priority=0, milestone=False,
    #                                      precedents=[], progress=0, subtasks=[])
    # task_database_manager.remove_task(task_id=13)
    # task_database_manager.set_progress(task_id=2, new_progress=100)
    # task_database_manager.set_start_date(task_id=9, new_start_date='2024-02-28')
    # task_database_manager.set_priority(task_id=2, new_priority=1)
    # task_database_manager.set_milestone(task_id=6, new_milestone_state=True)
    # task_database_manager.add_subtask(parent_id=10, child_id=11)
    # task_database_manager.remove_subtask(parent_id=11, child_id=12)
    # task_database_manager.add_precedent(task_id=6, precedent_id=5)
    # task_database_manager.remove_precedent(task_id=6, precedent_id=5)
    # task_database_manager.add_document(task_id=6, file_path='C:\\Users\\maxim\\Documents\\Git\\taskmanager\\main.py')
    # task_database_manager.remove_document(task_id=6, file_path='C:\\Users\\maxim\\Documents\\Git\\taskmanager\\main.py')
    # task_database_manager.clear_db()
    #
    # for entry in task_database_manager.get_every_task():
    #     print(entry)
    #
    # task_database_manager.close_db()
