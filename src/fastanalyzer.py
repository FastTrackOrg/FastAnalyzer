import rc_ressources
import os
import sys
import pickle

from plot import Plot
import fastanalysis as fa

from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QActionGroup, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem
from PySide2.QtCore import Signal, Slot, QFile, QStandardPaths, Qt, QTimer, QCoreApplication, QSettings
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_fastanalyzer import Ui_FastAnalyzer


dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


class FastAnalyzer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_FastAnalyzer()
        self.ui.setupUi(self)

        self.settings = QSettings()
        self.restoreGeometry(self.settings.value("main/geometry"))
        self.restoreState(self.settings.value("main/windowState"))

        # View menu
        self.ui.menuView.addSection(
    QCoreApplication.translate(
        "main", "View Mode"))
        viewMode = QActionGroup(self)
        stackView = QAction(QCoreApplication.translate("main", "Tabbed"), self)
        stackView.setCheckable(True)
        stackView.toggled.connect(
    lambda: self.ui.mdiArea.setViewMode(
        QMdiArea.TabbedView))
        viewMode.addAction(stackView)
        self.ui.menuView.addAction(stackView)
        winView = QAction(QCoreApplication.translate("main", "Windowed"), self)
        winView.setCheckable(True)
        winView.toggled.connect(
    lambda: self.ui.mdiArea.setViewMode(
        QMdiArea.SubWindowView))
        viewMode.addAction(winView)
        self.ui.menuView.addAction(winView)

        self.ui.menuView.addSection(
    QCoreApplication.translate(
        "main", "Window Mode"))
        cascadeView = QAction(
    QCoreApplication.translate(
        "main", "Cascaded"), self)
        cascadeView.triggered.connect(self.ui.mdiArea.cascadeSubWindows)
        winView.toggled.connect(cascadeView.setEnabled)
        self.ui.menuView.addAction(cascadeView)
        tileView = QAction(QCoreApplication.translate("main", "Tiled"), self)
        tileView.triggered.connect(self.ui.mdiArea.tileSubWindows)
        winView.toggled.connect(tileView.setEnabled)
        self.ui.menuView.addAction(tileView)

        if self.settings.value("main/mode", "0") == "0":
            winView.setChecked(True)
        else:
            tileView.setEnabled(False)
            cascadeView.setEnabled(False)
            stackView.setChecked(True)

        # File menu
        self.ui.actionOpen.triggered.connect(self.loadFile)
        self.ui.actionClose.triggered.connect(self.close)

        # Workspace menu
        self.ui.saveWorkspaceAction.triggered.connect(self.saveWorkspace)
        self.ui.loadWorkspaceAction.triggered.connect(self.loadWorkspace)
        self.ui.closeWorkspaceAction.triggered.connect(self.closeWorkspace)

        # Help menu
        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)
        self.ui.actionLicense.triggered.connect(lambda: QMessageBox.about(self, "License", "MIT  " \
                "License\nCopyright (c) 2022 FastTrackOrg\nPermission is hereby granted, free of  " \
                "charge, to any person obtaining a copy\nof this software and associated  " \
                "documentation files (the 'Software'), to deal\nin the Software without restriction, " \
                "including without limitation the rights\nto use, copy, modify, merge, publish, " \
                "distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons  " \
                "to whom the Software is\nfurnished to do so, subject to the following conditions: " \
                "\n\nThe above copyright notice and this permission notice shall be included in  " \
                "all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED " \
                "'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT " \
                "LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND " \
                "NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR " \
                "ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR " \
                "OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR " \
                "OTHER DEALINGS IN THE\nSOFTWARE."))

        # ToolBar
        self.addPlotAction = QAction(
            QCoreApplication.translate(
                "main", "Add Plot"), self)
        self.addPlotAction.triggered.connect(self.addPlot)
        self.ui.toolBar.addAction(self.addPlotAction)

        # Prepare Ui
        self.resetUi()
        self.workspacePath = self.settings.value("main/workspacePath", QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0] + "current")
        self.unSerializeWorkspace(self.workspacePath)


    def addPlot(self, params=None):
        subWindow = QMdiSubWindow(self)
        subWindow.setWidget(Plot(self.data, parent=self, params=params))
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWindowTitle("Plot {}".format(self.plotNumber))
        self.ui.mdiArea.addSubWindow(subWindow)
        self.plotNumber += 1
        if params:
            subWindow.restoreGeometry(params["geometry"])
            subWindow.widget().restoreState(params["state"])
        subWindow.show()

    def resetUi(self):
        self.plotNumber = 0
        self.ui.toolBar.setEnabled(False)
        self.ui.mdiArea.closeAllSubWindows()
        self.fileName = None
        self.data = None

    def loadFile(self):
        fileName, __ = QFileDialog.getOpenFileName(
                    self, QCoreApplication.translate(
                        "main", "Open tracking data"), QStandardPaths.standardLocations(
                        QStandardPaths.HomeLocation)[0], QCoreApplication.translate(
                        "main", "Tracking Files (*.db *.txt)"))
        if fileName:
            try:
                self.resetUi()
                self.fileName = fileName
                self.data = fa.Load(self.fileName)
                self.ui.statusbar.showMessage(QCoreApplication.translate("main", "{} loaded with success".format(self.fileName)))
                self.ui.toolBar.setEnabled(True)
                self.loadDatainTableWin()
            except Exception as e:
                self.ui.statusbar.showMessage(QCoreApplication.translate("main", "{} can't be parsed {}".format(self.fileName, e)))
                self.resetUi()

    def loadDatainTableWin(self):
        table = QTableWidget(len(self.data.getDataframe()), len(self.data.getDataframe().columns), self)
        for i, j in enumerate(self.data.getDataframe().columns.values.tolist()):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(j))
        for col, __ in enumerate(self.data.getDataframe().columns):
            for row, val in enumerate(self.data.getDataframe().iloc[:, col].values):
                table.setItem(row, col, QTableWidgetItem(str(val)))

        subWindow = QMdiSubWindow(self)
        subWindow.setWidget(table)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWindowTitle("Data Table")
        self.ui.mdiArea.addSubWindow(subWindow)
        subWindow.show()
        subWindow.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint) # Need to be set after show()

    def serializeWorkspace(self, path):
        wins = []
        for i in self.ui.mdiArea.subWindowList(QMdiArea.StackingOrder):
            if i.windowTitle() != "Data Table":
                var = i.widget().savePlotState()
                var["geometry"] = i.saveGeometry()
                var["state"] = i.widget().saveState()
                wins.append(var)

        with open(path, 'wb') as file:
            workspace = {"name": path,"filename": self.fileName, "wins": wins}
            self.workspacePath = workspace["name"]
            pickle.dump(workspace, file)

    def unSerializeWorkspace(self, path):
        try:
            if QFile(path).exists():
                with open(path, 'rb') as file:
                    workspace = pickle.load(file)
                    self.fileName = workspace["filename"]
                    self.data = fa.Load(self.fileName)
                    self.workspacePath = workspace["name"]
                    self.ui.statusbar.showMessage(QCoreApplication.translate("main", "{} loaded with success".format(self.workspacePath)))
                    self.ui.toolBar.setEnabled(True)
                    self.loadDatainTableWin()
                    for i in workspace["wins"]:
                        self.addPlot(i)
        except Exception as e:
            self.ui.statusbar.showMessage(QCoreApplication.translate("main", "Last workspace can't be recovered {}".format(e)))
            self.resetUi()

    def saveWorkspace(self):
        fileName, __ = QFileDialog.getSaveFileName(
                    self, QCoreApplication.translate(
                        "main", "Save Workspace"), QStandardPaths.standardLocations(
                        QStandardPaths.HomeLocation)[0] + "/fastanalyzer.workspace", QCoreApplication.translate(
                        "main", "Workspace (*.workspace)"))
        if fileName:
            self.serializeWorkspace(fileName)


    def loadWorkspace(self):
        fileName, __ = QFileDialog.getOpenFileName(
                    self, QCoreApplication.translate(
                        "main", "Load Workspace"), QStandardPaths.standardLocations(
                        QStandardPaths.HomeLocation)[0], QCoreApplication.translate(
                        "main", "Workspace (*.workspace)"))
        if fileName:
            self.resetUi()
            self.unSerializeWorkspace(fileName)

    def closeWorkspace(self):
        msgBox = QMessageBox()
        msgBox.setText("The workspace has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec_()
        if ret == QMessageBox.Save:
            self.saveWorkspace()
            self.resetUi()
        elif ret == QMessageBox.Discard:
            self.resetUi()
        elif ret == QMessageBox.Cancel:
            ...

    def closeEvent(self, event):
        self.serializeWorkspace(self.workspacePath)
        self.saveSettings()
        event.accept()

    def saveSettings(self):
        self.settings.setValue("main/geometry", self.saveGeometry());
        self.settings.setValue("main/windowState", self.saveState());
        self.settings.setValue("main/mode", self.ui.mdiArea.viewMode());
        self.settings.setValue("main/workspacePath", self.workspacePath);


if __name__ == "__main__":
    app=QApplication([])
    QFontDatabase.addApplicationFont(":/assets/RobotoCondensed-Regular.ttf")
    QFontDatabase.addApplicationFont(":/assets/Roboto-Regular.ttf")
    app.setFont(QFont("Roboto"))
    app.setApplicationName("FastAnalyzer")
    app.setApplicationVersion("0.0.0")
    app.setOrganizationName("FastTrackOrg")
    app.setOrganizationDomain("fasttrack.sh")
    widget=FastAnalyzer()
    widget.show()
    sys.exit(app.exec_())