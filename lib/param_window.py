from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication, QCursor
from PySide6.QtWidgets import QLineEdit, QGridLayout, QLabel, QPushButton, QCheckBox, QDialog, QMessageBox, QComboBox, \
    QFileDialog


class ParamDialog(QDialog):

    def __init__(self, main_win):
        super(ParamDialog, self).__init__()

        self.main_win = main_win

        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.title_font_size = 14
        self.subtitle_font_size = 11
        self.item_font_size = 9

        self.modifying = False

        grid = QGridLayout()

        git_db_title_line = 0
        git_db_activated_line = git_db_title_line + 1
        git_db_path_line = git_db_activated_line + 1
        notif_title_line = git_db_path_line + 1
        notif_activated_line = notif_title_line + 1
        notif_period_line = notif_activated_line + 1
        gantt_title_line = notif_period_line + 1
        gantt_activated_line = gantt_title_line + 1
        gantt_end_date_line = gantt_activated_line + 1
        gantt_duration_line = gantt_end_date_line + 1
        enter_btn_line = gantt_duration_line + 1

        lbl = QLabel("Git Database")
        lbl.setFont(QFont('AnyStyle', self.title_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, git_db_title_line, 0, 1, 3)

        lbl = QLabel("Activated")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, git_db_activated_line, 0)

        self.git_db_activated_checkbox = QCheckBox()
        self.git_db_activated_checkbox.stateChanged.connect(self.git_db_activated_checkbox_state_changed)
        grid.addWidget(self.git_db_activated_checkbox, git_db_activated_line, 1)

        lbl = QLabel("Database path")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, git_db_path_line, 0)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedHeight(30)
        # self.browse_btn.setFixedWidth(90)
        self.browse_btn.setFont(QFont('AnyStyle', self.item_font_size))
        self.browse_btn.clicked.connect(self.browse_btn_clicked)
        grid.addWidget(self.browse_btn, git_db_path_line, 1)

        self.path_lbl = QLabel()
        self.path_lbl.setFont(QFont('AnyStyle', self.item_font_size))
        self.path_lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.path_lbl, git_db_path_line, 2)

        lbl = QLabel("Notifications")
        lbl.setFont(QFont('AnyStyle', self.title_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, notif_title_line, 0, 1, 3)

        lbl = QLabel("Activated")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, notif_activated_line, 0)

        self.notif_activated_checkbox = QCheckBox()
        self.notif_activated_checkbox.stateChanged.connect(self.notif_activated_checkbox_state_changed)

        grid.addWidget(self.notif_activated_checkbox, notif_activated_line, 1)

        lbl = QLabel("Every...")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, notif_period_line, 0)

        self.time_line_edit = QLineEdit()
        self.time_line_edit.setFixedWidth(50)
        self.time_line_edit.setFixedHeight(30)
        self.time_line_edit.setFont(QFont('AnyStyle', self.item_font_size))
        grid.addWidget(self.time_line_edit, notif_period_line, 1)

        self.time_unit_combobox = QComboBox()
        self.time_unit_combobox.setFixedWidth(100)
        self.time_unit_combobox.setFixedHeight(30)
        self.time_unit_combobox.setFont(QFont('AnyStyle', self.item_font_size))
        grid.addWidget(self.time_unit_combobox, notif_period_line, 2)

        time_units = ["minutes", "hours"]
        for i in range(0, len(time_units)):
            self.time_unit_combobox.insertItem(i, str(time_units[i]))

        lbl = QLabel("GANTT")
        lbl.setFont(QFont('AnyStyle', self.title_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, gantt_title_line, 0, 1, 3)

        lbl = QLabel("Activated")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, gantt_activated_line, 0)

        self.gantt_activated_checkbox = QCheckBox()
        self.gantt_activated_checkbox.stateChanged.connect(self.gantt_activated_checkbox_state_changed)

        grid.addWidget(self.gantt_activated_checkbox, gantt_activated_line, 1)

        lbl = QLabel("If no end date:")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, gantt_end_date_line, 0)

        self.no_end_date_combobox = QComboBox()
        # self.no_end_date_combobox.setFixedWidth(100)
        self.no_end_date_combobox.setFixedHeight(30)
        self.no_end_date_combobox.setFont(QFont('AnyStyle', self.item_font_size))
        grid.addWidget(self.no_end_date_combobox, gantt_end_date_line, 1, 1, 2)

        no_end_date_choices = ["Apply duration", "Set to today"]
        for i in range(0, len(no_end_date_choices)):
            self.no_end_date_combobox.insertItem(i, str(no_end_date_choices[i]))

        lbl = QLabel("Duration (work days)")
        lbl.setFont(QFont('AnyStyle', self.subtitle_font_size))
        lbl.setAlignment(Qt.AlignCenter)
        grid.addWidget(lbl, gantt_duration_line, 0)

        self.duration_line_edit = QLineEdit()
        self.duration_line_edit.setFixedWidth(50)
        self.duration_line_edit.setFixedHeight(30)
        self.duration_line_edit.setFont(QFont('AnyStyle', self.item_font_size))
        grid.addWidget(self.duration_line_edit, gantt_duration_line, 1)

        self.no_end_date_combobox.currentTextChanged.connect(self.no_end_date_combobox_changed)

        enter_btn = QPushButton("Enter")
        enter_btn.setFixedHeight(30)
        # enter_btn.setFixedWidth(90)
        enter_btn.setFont(QFont('AnyStyle', self.subtitle_font_size))
        enter_btn.clicked.connect(self.enter_btn_clicked)
        grid.addWidget(enter_btn, enter_btn_line, 0, 1, 3)

        self.setLayout(grid)
        enter_btn.setDefault(True)

    def showEvent(self, event):
        if self.main_win.os == 'linux':
            self.move(
                QGuiApplication.screenAt(QCursor.pos()).availableGeometry().center() - self.frameGeometry().center())

        self.modifying = True
        if self.main_win.config["git_database"]:
            self.git_db_activated_checkbox.setChecked(True)
            self.browse_btn.setEnabled(True)
        else:
            self.git_db_activated_checkbox.setChecked(False)
            self.browse_btn.setEnabled(False)
        self.path_lbl.setText(self.main_win.config["database_path"])

        if self.main_win.config["notif"]:
            self.notif_activated_checkbox.setChecked(True)
            self.time_line_edit.setEnabled(True)
            self.time_unit_combobox.setEnabled(True)
        else:
            self.notif_activated_checkbox.setChecked(False)
            self.time_line_edit.setEnabled(False)
            self.time_unit_combobox.setEnabled(False)
        self.time_line_edit.setText(self.main_win.config["period"])
        self.time_unit_combobox.setCurrentText(self.main_win.config["unit"])

        if self.main_win.config["gantt"]:
            self.gantt_activated_checkbox.setChecked(True)
            self.no_end_date_combobox.setEnabled(True)
            self.duration_line_edit.setEnabled(True)
        else:
            self.gantt_activated_checkbox.setChecked(False)
            self.no_end_date_combobox.setEnabled(False)
            self.duration_line_edit.setEnabled(False)
        self.no_end_date_combobox.setCurrentText(self.main_win.config["no_end_date_format"])
        self.duration_line_edit.setText(self.main_win.config["no_end_date"])

    def hideEvent(self, event):
        if self.modifying:
            button = QMessageBox.warning(self,
                                         "Modifying settings",
                                         "Changes will not be saved",
                                         buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                         defaultButton=QMessageBox.Ok)
            if button == QMessageBox.Ok:
                self.modifying = False
            elif button == QMessageBox.Cancel:
                self.show()

    def git_db_activated_checkbox_state_changed(self):
        if self.git_db_activated_checkbox.isChecked():
            self.browse_btn.setEnabled(True)
        else:
            self.browse_btn.setEnabled(False)

    def browse_btn_clicked(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select database")

        if file:
            file_name = file[0].split("/")[-1:][0]
            last_folder_name = file[0].split("/")[-2:-1][0]
            relative_path = f"../{last_folder_name}/{file_name}"
            self.path_lbl.setText(relative_path)

    def notif_activated_checkbox_state_changed(self):
        if self.notif_activated_checkbox.isChecked():
            self.time_line_edit.setEnabled(True)
            self.time_unit_combobox.setEnabled(True)
        else:
            self.time_line_edit.setEnabled(False)
            self.time_unit_combobox.setEnabled(False)

    def gantt_activated_checkbox_state_changed(self):
        if self.gantt_activated_checkbox.isChecked():
            self.duration_line_edit.setEnabled(True)
            self.no_end_date_combobox.setEnabled(True)
        else:
            self.duration_line_edit.setEnabled(False)
            self.no_end_date_combobox.setEnabled(False)

    def no_end_date_combobox_changed(self, text):
        if text == "Set to today":
            self.duration_line_edit.setEnabled(False)
        else:
            self.duration_line_edit.setEnabled(True)

    def enter_btn_clicked(self):

        if self.modifying:
            button = QMessageBox.warning(self,
                                         "Modifying settings",
                                         "Changes will be saved",
                                         buttons=QMessageBox.Cancel | QMessageBox.Ok,
                                         defaultButton=QMessageBox.Ok)
            if button == QMessageBox.Ok:
                self.main_win.config["git_database"] = self.git_db_activated_checkbox.isChecked()
                self.main_win.config["database_path"] = self.path_lbl.text()
                self.main_win.config["notif"] = self.notif_activated_checkbox.isChecked()
                self.main_win.config["period"] = self.time_line_edit.text()
                self.main_win.config["unit"] = self.time_unit_combobox.currentText()
                self.main_win.config["gantt"] = self.gantt_activated_checkbox.isChecked()
                self.main_win.config["no_end_date_format"] = self.no_end_date_combobox.currentText()
                self.main_win.config["no_end_date"] = self.duration_line_edit.text()
                self.modifying = False

                self.main_win.update_config()
                self.hide()

        else:
            self.hide()
