import yaml
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem, QDialog, QVBoxLayout, QMessageBox, \
    QInputDialog, QAction, QMenu

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
