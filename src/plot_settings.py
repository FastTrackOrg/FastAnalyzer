from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide2.QtCore import Signal, QFile, QStandardPaths, Qt, QTimer
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_plot_settings import Ui_PlotSettings


class PlotSettings(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_PlotSettings()
        self.ui.setupUi(self)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
