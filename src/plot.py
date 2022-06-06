from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide2.QtCore import Signal, QFile, QCoreApplication, QStandardPaths, Qt, QTimer
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
from ui_plot import Ui_Plot

from plot_settings import PlotSettings


class Plot(QMainWindow):
    def __init__(self, settingsWindow, parent=None):
        super().__init__(parent)
        self.ui = Ui_Plot()
        self.ui.setupUi(self)
        self.settingsWindow = PlotSettings(self)
        self.ui.settingsDock.setWidget(self.settingsWindow)

    def __del__(self):
        self.settingsWindow.close()
