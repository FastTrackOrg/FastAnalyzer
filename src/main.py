import rc_ressources
import os
import sys

from plot import Plot
import fastanalysis as fa

from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QActionGroup, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem
from PySide2.QtCore import Signal, Slot, QFile, QStandardPaths, Qt, QTimer, QCoreApplication
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_main import Ui_FastAnalyzer


dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


class FastAnalyzer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_FastAnalyzer()
        self.ui.setupUi(self)

        # View menu
        self.ui.menuView.addSection(
    QCoreApplication.translate(
        "main", "View Mode"))
        viewMode = QActionGroup(self)
        stackView = QAction(QCoreApplication.translate("main", "Tabbed"), self)
        stackView.setCheckable(True)
        stackView.triggered.connect(
    lambda: self.ui.mdiArea.setViewMode(
        QMdiArea.TabbedView))
        viewMode.addAction(stackView)
        self.ui.menuView.addAction(stackView)
        winView = QAction(QCoreApplication.translate("main", "Windowed"), self)
        winView.setCheckable(True)
        winView.triggered.connect(
    lambda: self.ui.mdiArea.setViewMode(
        QMdiArea.SubWindowView))
        viewMode.addAction(winView)
        self.ui.menuView.addAction(winView)
        winView.setChecked(True)

        self.ui.menuView.addSection(
    QCoreApplication.translate(
        "main", "Window Mode"))
        winMode = QActionGroup(self)
        cascadeView = QAction(
    QCoreApplication.translate(
        "main", "Cascaded"), self)
        cascadeView.setCheckable(True)
        cascadeView.triggered.connect(self.ui.mdiArea.cascadeSubWindows)
        winMode.addAction(cascadeView)
        self.ui.menuView.addAction(cascadeView)
        tileView = QAction(QCoreApplication.translate("main", "Tiled"), self)
        tileView.setCheckable(True)
        tileView.triggered.connect(self.ui.mdiArea.tileSubWindows)
        winMode.addAction(tileView)
        self.ui.menuView.addAction(tileView)
        tileView.setChecked(True)

        # File menu
        self.ui.actionOpen.triggered.connect(self.loadFile)
        self.ui.actionClose.triggered.connect(self.close)

        # Help menu
        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)
        self.ui.actionLicense.triggered.connect(lambda: QMessageBox.about(self.ui, "License", "MIT License\nCopyright (c) 2022 FastTrackOrg\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the 'Software'), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE."))

        # ToolBar
        self.addPlotAction = QAction(
            QCoreApplication.translate(
                "main", "Add Plot"), self)
        self.addPlotAction.triggered.connect(self.addPlot)
        self.ui.toolBar.addAction(self.addPlotAction)

        # Prepare Ui
        self.resetUi()


    def addPlot(self):
        subWindow = QMdiSubWindow(self)
        subWindow.setWidget(Plot(self.data, self))
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWindowTitle("Plot {}".format(self.plotNumber))
        self.ui.mdiArea.addSubWindow(subWindow)
        self.plotNumber += 1
        subWindow.show()

    def resetUi(self):
        self.plotNumber = 0
        self.addPlotAction.setEnabled(False)
        self.ui.mdiArea.closeAllSubWindows()

    def loadFile(self):
        fileName, __ = QFileDialog.getOpenFileName(
                    self, QCoreApplication.translate(
                        "main", "Open tracking data"), QStandardPaths.standardLocations(
                        QStandardPaths.HomeLocation)[0], QCoreApplication.translate(
                        "main", "Tracking Files (*.db *.txt)"))
        if fileName:
            try:
                self.resetUi()
                self.data = fa.Load(fileName)
                self.ui.statusbar.showMessage(QCoreApplication.translate("main", "{} loaded with success".format(fileName)))
                self.addPlotAction.setEnabled(True)
                self.loadDatainTableWin()
            except Exception as e:
                self.ui.statusbar.showMessage(QCoreApplication.translate("main", "{} can't be parsed {}".format(fileName, e)))
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




if __name__ == "__main__":
    app=QApplication([])
    QFontDatabase.addApplicationFont(":/assets/RobotoCondensed-Regular.ttf")
    QFontDatabase.addApplicationFont(":/assets/Roboto-Regular.ttf")
    app.setFont(QFont("Roboto"))
    widget=FastAnalyzer()
    widget.show()
    sys.exit(app.exec_())
