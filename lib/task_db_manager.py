import os
from peewee import *
from datetime import datetime, date

from PySide6.QtCore import QObject


# Define a custom field type for storing a list of strings
class ListField(Field):
    def db_value(self, value):
        if value is not None:
            return ','.join(value)

    def python_value(self, value):
        if value is not None:
            return value.split(',')


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
    subtasks = ListField()  # list of sub-tasks, if any this task became a section

    class Meta:
        database = None  # SQLite database file


class TaskDatabaseManager(QObject):

    def __init__(self, db_path: str):
        super().__init__()

        self.tasks_db = SqliteDatabase(db_path)

        Task._meta.database = self.tasks_db

        self.tasks_db.connect()
        if not os.path.exists(f'lib/{db_path}'):
            self.tasks_db.create_tables([Task], safe=True)

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
    def get_every_task():
        return Task.select()


task_database_manager = TaskDatabaseManager('task_database.db')

ref = task_database_manager.add_task(name="Test2", documents=["tasks.db", "again.ini"])
print(f'{ref=}')

for entry in task_database_manager.get_every_task():
    print(entry.name, entry.documents)


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

