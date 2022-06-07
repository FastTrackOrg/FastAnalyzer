from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide2.QtCore import Signal, QFile, QCoreApplication, QStandardPaths, Qt, QTimer
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
from ui_plot import Ui_Plot

from plot_settings import PlotSettings
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns


class Plot(QMainWindow):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.ui = Ui_Plot()
        self.ui.setupUi(self)
        self.settingsWindow = PlotSettings(self)
        self.ui.settingsDock.setWidget(self.settingsWindow)

        self.canvas = FigureCanvas(Figure(figsize=(600*1/plt.rcParams['figure.dpi'], 200*1/plt.rcParams['figure.dpi'])))
        self.setCentralWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.addToolBar(NavigationToolbar(self.canvas, self))

        self.settingsWindow.redraw.connect(self.update)
        self.settingsWindow.plotChanged()

    def update(self, params):
        self.ax.clear()
        self.plot(**params)
        self.setLabel(**params)
        self.setTitle(**params)
        self.canvas.draw_idle()

    def plot(self, plotType, plotKey, idPlot, idCustom, **kwargs):
        if idPlot == "Pool":
            mode = None
            data = self.data.getDataframe()
        elif idPlot == "All":
            mode = "\"id\""
            data = self.data.getDataframe()
        else:
            mode = "\"id\""
            data = self.data.getObjects(eval("[{}]".format(idCustom)))

        eval("sns.{}(data=data.reset_index(drop=True), x=\"{}\", hue={}, ax=self.ax)".format(plotType, plotKey, mode))

    def setLabel(self, xLabel, yLabel, labelSize, **kwargs):
        self.ax.set_xlabel(xLabel, fontsize=labelSize)
        self.ax.set_ylabel(yLabel, fontsize=labelSize)

    def setTitle(self, title, titleSize,**kwargs):
        self.ax.set_title(title, fontsize=titleSize)

