import os

from PySide6.QtCore import Qt, QDateTime, QDate
from PySide6.QtGui import QFont, QTextOption, QAction
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDateEdit, \
    QDialog, QPlainTextEdit, QMessageBox, QComboBox, QFileDialog, QMenu

from lib.style import select_icon


class AddTaskDialog(QDialog):

    def __init__(self, main_win):
        super(AddTaskDialog, self).__init__()

        self.mainWin = main_win

        self.modifying = False
        self.task = None
        self.documentsList = []

        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Ajouter une tâche")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.titleFontSize = 14
        self.subtitleFontSize = 11
        self.itemFontSize = 9.5

        self.last_dir = "/"

        grid = QGridLayout()

        lbl = QLabel("Nom")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 0, 0)

        self.nameTextEdit = QLineEdit()
        self.nameTextEdit.setMinimumWidth(240)
        self.nameTextEdit.setFixedHeight(30)
        self.nameTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.nameTextEdit, 0, 1)

        lbl = QLabel("Description")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 1, 0)

        self.descTextEdit = QPlainTextEdit()
        self.descTextEdit.setMinimumWidth(240)
        self.descTextEdit.setMinimumHeight(110)
        self.descTextEdit.setWordWrapMode(QTextOption.WordWrap.WrapAtWordBoundaryOrAnywhere)
        self.descTextEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.descTextEdit, 1, 1)

        lbl = QLabel("Priorité")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 2, 0)

        self.priorityComboBox = QComboBox()
        self.priorityComboBox.setMinimumWidth(240)
        self.priorityComboBox.setFixedHeight(30)
        self.priorityComboBox.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.priorityComboBox, 2, 1)

        priority_degrees = ["Normal", "Pressant", "Urgent"]
        for i in range(0, len(priority_degrees)):
            self.priorityComboBox.insertItem(i, str(priority_degrees[i]))

        lbl = QLabel("Date de début")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 3, 0)

        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setDateTime(QDateTime.currentDateTime())
        self.startDateEdit.setMinimumWidth(210)
        self.startDateEdit.setFixedHeight(30)
        self.startDateEdit.setFont(QFont('AnyStyle', self.itemFontSize))
        grid.addWidget(self.startDateEdit, 3, 1)

        lbl = QLabel("Date de fin")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 4, 0)

        end_date_layout = QHBoxLayout()

        self.endDateCheckBox = QCheckBox()
        self.endDateCheckBox.stateChanged.connect(self.end_date_checkbox_state_changed)

        self.endDateEdit = QDateEdit(calendarPopup=True)
        self.endDateEdit.setEnabled(False)
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())
        self.endDateEdit.setMinimumWidth(210)
        self.endDateEdit.setFixedHeight(30)
        self.endDateEdit.setFont(QFont('AnyStyle', self.itemFontSize))

        end_date_layout.addWidget(self.endDateCheckBox, 0)
        end_date_layout.addWidget(self.endDateEdit, 1)

        grid.addLayout(end_date_layout, 4, 1)

        lbl = QLabel("Documents")
        lbl.setFont(QFont('AnyStyle', self.subtitleFontSize))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, 5, 0)

        browse_layout = QHBoxLayout()

        browse_btn = QPushButton("Parcourir")
        browse_btn.setFixedHeight(30)
        # browse_btn.setFixedWidth(90)
        browse_btn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        browse_btn.clicked.connect(self.browse_btn_clicked)
        browse_layout.addWidget(browse_btn, 0)

        self.filesLayout = QGridLayout()
        self.filesLayoutRow = 0
        self.filesLayoutColumn = 0
        self.filesLabels = []

        browse_layout.addLayout(self.filesLayout)

        grid.addLayout(browse_layout, 5, 1)

        enter_task_btn = QPushButton("Entrer")
        enter_task_btn.setFixedHeight(30)
        # enter_task_btn.setFixedWidth(90)
        enter_task_btn.setFont(QFont('AnyStyle', self.subtitleFontSize))
        enter_task_btn.clicked.connect(self.enter_task_btn_clicked)
        grid.addWidget(enter_task_btn, 6, 0, 1, 2)

        self.setLayout(grid)
        enter_task_btn.setDefault(True)

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
            msg.buttonClicked.connect(self.on_hide_msg_box_btn_clicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec()

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

    def on_hide_msg_box_btn_clicked(self, button):
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

    def end_date_checkbox_state_changed(self):
        if self.endDateCheckBox.isChecked():
            self.endDateEdit.setEnabled(True)
        else:
            self.endDateEdit.setEnabled(False)

    def enter_task_btn_clicked(self):
        task_name = self.nameTextEdit.text()
        task_priority = self.priorityComboBox.currentText()
        task_description = self.descTextEdit.toPlainText()
        task_start_date = self.startDateEdit.date().toString(Qt.ISODate)
        if not self.endDateCheckBox.isChecked():
            task_end_date = "-"
        else:
            task_end_date = self.endDateEdit.date().toString(Qt.ISODate)

        self.task = {"Name": task_name, "Description": task_description, "Priority": task_priority,
                     "StartDate": task_start_date, "EndDate": task_end_date, "Check": 0,
                     "Documents": self.documentsList}

        if self.modifying:
            msg = QMessageBox()
            msg.setWindowTitle("Modification de tâche")
            msg.setText("La tâche va être modifiée")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.on_enter_msg_box_btn_clicked)

            msg.setButtonText(QMessageBox.Cancel, "Annuler")
            msg.setButtonText(QMessageBox.Ok, "OK")
            msg.exec()

        else:
            self.mainWin.create_task(self.task)
            self.hide()

    def on_enter_msg_box_btn_clicked(self, button):
        if button.text() == "OK":
            self.mainWin.update_task(self.task)
            self.modifying = False
            self.hide()

    def modify_task(self, task):
        self.nameTextEdit.setText(task["Name"])
        self.descTextEdit.setPlainText(task["Description"])
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

        files_paths = task["Documents"]

        self.display_selected_documents(files_paths)
        self.setWindowTitle("Modifier une tâche")
        self.modifying = True
        self.show()

    def browse_btn_clicked(self):
        file = QFileDialog.getOpenFileNames(parent=self,
                                            caption="Sélectionner un ou plusieurs fichier(s)",
                                            dir=self.last_dir)#,
                                            # options=QFileDialog.DontUseNativeDialog)
        # if file:
        #     files_paths = file[0]
        #     self.display_selected_documents(files_paths)

        if file:
            if file[0]:
                files_paths = file[0]
                self.last_dir = os.path.dirname(files_paths[0])  # + "/"

                self.display_selected_documents(files_paths)

        # get a folder :
        # folder = QFileDialog.getExistingDirectory(parent=self, caption="Sélectionner un dossier")

    def display_selected_documents(self, files_paths):
        if len(files_paths) > 0:

            for document in files_paths:

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
            # context_menu.exec_(lbl.mapToGlobal(pos))
            context_menu.exec(lbl.mapToGlobal(pos))

        return show_context_menu
