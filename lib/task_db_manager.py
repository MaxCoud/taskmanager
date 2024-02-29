import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QFont, Qt, QGuiApplication, QCursor, QCloseEvent, QStandardItem, QIcon
from PySide6.QtWidgets import QGridLayout, QWidget, QMainWindow, QTreeView, QLabel, QTreeWidget, QTabWidget, \
    QApplication
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

        self.icons = load_icons(Path(__file__).resolve().parent.parent)

        database_path = f'{Path(__file__).resolve().parent}{self.slash}task_database.db'
        self.task_database_manager = TaskDatabaseManager(database_path)

        self.setWindowModality(Qt.ApplicationModal)

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 10

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

        main_window = QWidget()
        main_window.setLayout(layout)  # running_layout
        self.setCentralWidget(main_window)
        # self.setLayout(running_layout)

        self.update_changes()
        self.update_tree()

        self.showMaximized()

        if self.os == 'linux':
            # --- center window ---
            # - on primary screen -
            # self.move(QGuiApplication.primaryScreen().availableGeometry().center() - self.frameGeometry().center())
            # - on screen where mouse pointer is -
            self.move(QGuiApplication.screenAt(
                QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())
            # ---------------------

    def on_project_tree_clicked(self):
        pass

    def show_tree_context_menu(self):
        pass

    def list_tree_changed(self):
        pass

    def list_tree_item_clicked(self):
        pass

    def finished_tasks_tree_changed(self):
        pass

    def finished_tasks_tree_item_clicked(self):
        pass

    def modify_task_btn_clicked(self):
        pass

    def show_lists_context_menu(self):
        pass

    def custom_sort_by_column(self):
        pass

    def update_changes(self):
        pass

    def update_tree(self):

        self.model.clear()

        def add_item(parent, data):
            item = QStandardItem(data.name)
            item.setData(data)
            item.setEditable(False)
            parent.appendRow(item)

            running_tasks = 0
            for subtask_id in data.subtasks:
                if self.task_database_manager.get_task(subtask_id).progress != 100:
                    running_tasks += 1

            if running_tasks == 0:
                item.setIcon(QIcon(self.icons["tick"]))
            elif running_tasks > 20:
                item.setIcon(QIcon(self.icons["folder"]))
            else:
                item.setIcon(QIcon(self.icons[running_tasks]))

            for subtask_id in data.subtasks:
                if len(self.task_database_manager.get_task(subtask_id).subtasks) > 0:
                    add_item(item, self.task_database_manager.get_task(subtask_id))

        # create the root item and add it to the model
        root_item = QStandardItem(self.task_database_manager.get_task(task_id=1).name)
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
        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        self.task_database_manager.close_db()


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

    ref = AutoField()  # primary key
    name = CharField()  # task name
    description = CharField()  # task description
    start_date = DateField()  # task start date
    end_date = DateField()  # task end date
    documents = ListField()  # list of documents
    priority = IntegerField()  # task priority
    milestone = BooleanField()  # task is milestone or not
    precedents = ListField()  # list of tasks that need to be done before this one
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

    @staticmethod
    def add_task(name="", description="", start_date="", end_date="", documents=None, priority=0,
                 milestone=False, precedents=None, progress=0, subtasks=None) -> Task.ref:
        if subtasks is None:
            subtasks = []
        if precedents is None:
            precedents = []
        if documents is None:
            documents = []
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
    def add_subtask(parent_id, child_id):
        task = Task.get(Task.ref == parent_id)
        task.subtasks.append(child_id)
        task.save()

    @staticmethod
    def get_task(task_id):
        return Task.get(Task.ref == task_id)

    @staticmethod
    def get_every_task(with_root=False):
        if with_root:
            return Task.select()
        else:
            return Task.select().where(Task.ref != 1)

    @staticmethod
    def remove_task(task_id):
        try:
            task_to_remove = Task.get(Task.ref == task_id)
            task_to_remove.delete_instance()
        except Task.DoesNotExist:
            print(f"Task with ref={task_id} does not exists in database")

    @staticmethod
    def update_progress(task_id, new_progress):
        task = Task.get(Task.ref == task_id)
        task.progress = new_progress
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
    # task_database_manager.update_progress(task_id=2, new_progress=100)
    # task_database_manager.add_subtask(10, 11)
    # task_database_manager.clear_db()
    #
    # for entry in task_database_manager.get_every_task():
    #     print(entry)
    #
    # task_database_manager.close_db()




# # Define your model
# class MyModel(Model):
#     name = CharField()
#     tags = ListField()  # Attribute that is a list of strings
#
#     class Meta:
#         database = SqliteDatabase('my_database.db')  # SQLite database file
#
#
# # Create tables
# MyModel.create_table()
#
# # Example usage
# tags_list = ['tag1', 'tag2', 'tag3']
# instance = MyModel.create(name='example', tags=tags_list)
#
# # Querying
# for entry in MyModel.select():
#     print(entry.name, entry.tags)

