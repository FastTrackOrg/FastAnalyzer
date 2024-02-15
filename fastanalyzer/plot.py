from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide6.QtCore import Signal, QFile, QCoreApplication, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPen, QPainter, QAction, QPalette, QPixmap, QFont, QFontDatabase
from ui_plot import Ui_Plot

from plot_settings import PlotSettings
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from statannotations.Annotator import Annotator


class Plot(QMainWindow):
    def __init__(self, data, parent=None, params=None):
        super().__init__(parent)
        self.data = data
        self.ui = Ui_Plot()
        self.ui.setupUi(self)
        self.settingsWindow = PlotSettings(
            self, params=params, keys=self.data.getDataframe().columns.values.tolist())
        self.ui.settingsDock.setWidget(self.settingsWindow)

        self.canvas = FigureCanvas(
            Figure(
                figsize=(
                    600 *
                    1 /
                    plt.rcParams['figure.dpi'],
                    200 *
                    1 /
                    plt.rcParams['figure.dpi'])))
        self.setCentralWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.mplToolBar = NavigationToolbar(self.canvas, self)
        self.mplToolBar.setObjectName("Mpl toolbar")
        self.addToolBar(self.mplToolBar)

        self.settingsWindow.redraw.connect(self.update)
        self.settingsWindow.plotChanged()

    def update(self, params):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.ax.clear()
        params = {i: ("\"{}\"".format(j) if i in [
                      "plotKey", "plotKeyX"] else j) for i, j in params.items()}
        params = {i: (None if j == "\"None\"" else j)
                  for i, j in params.items()}
        self.plot(**params)
        self.setLabel(**params)
        self.setTitle(**params)
        self.canvas.draw_idle()
        QApplication.restoreOverrideCursor()

    def plot(self, plotType, plotKey, plotId, customId,
             plotKeyX, lowLevelApi, pTest, pPairs, **kwargs):
        try:
            if plotId == "Pool":
                mode = None
                data = self.data.getDataframe().dropna()
                order = None
            elif plotId == "All":
                mode = "\"id\""
                data = self.data.getDataframe().dropna()
                data = data.astype({'id': 'str'}, copy=False)
                order = list(data["id"].unique())
            else:
                mode = "\"id\""
                data = self.data.getObjects(
                    eval("[{}]".format(customId))).dropna()
                data = data.astype({'id': 'str'}, copy=False)
                order = list(data["id"].unique())

            if plotType in self.settingsWindow.univariateDistPlot:  # Univariate distribution
                eval(
                    "sns.{}(data=data, x={}, y={}, hue={}, ax=self.ax, fill=True, **{})".format(
                        plotType,
                        plotKey,
                        plotKeyX,
                        mode,
                        lowLevelApi))
            elif plotType in self.settingsWindow.statPlot:  # Descriptive
                eval(
                    "sns.{}(data=data, y={}, x={}, ax=self.ax, order=order, **{})".format(
                        plotType, plotKey, mode, lowLevelApi))
                if pTest != "None" and plotId != "Pool":
                    annotator = eval(
                        "Annotator(self.ax, [(str(i[0]), str(i[1])) for i in [{}]], data=data, y={}, x={}, order=order, verbose=False)".format(
                            pPairs, plotKey, mode))
                    eval(
                        "annotator.configure(test=\"{}\", text_format='star', loc='inside')".format(pTest))
                    annotator.apply_and_annotate()
                    pLegend = "p-value annotation legend:\nns: p <= 1.00e+00\n*: 1.00e-02 < p <= 5.00e-02\n**: 1.00e-03 < p <= 1.00e-02\n***: 1.00e-04 < p <= 1.00e-03\n****: p <= 1.00e-04"  # No custom threshold allowed
                    detail = pLegend + "\n\n" + "\n".join([" vs. ".join(
                        [struct["label"]for struct in i.structs]) + ": " + i.formatted_output for i in annotator.annotations])
                    self.settingsWindow.ui.pDetail.setPlainText(detail)

            self.ui.statusbar.showMessage(
                QCoreApplication.translate(
                    "main", "Plotted with success"))

        except Exception as e:
            self.ui.statusbar.showMessage(
                QCoreApplication.translate(
                    "plot", "Error while plotting: {}".format(e)))

    def setLabel(self, xLabel, yLabel, labelSize, **kwargs):
        self.ax.set_xlabel(xLabel, fontsize=labelSize)
        self.ax.set_ylabel(yLabel, fontsize=labelSize)

    def setTitle(self, title, titleSize, **kwargs):
        self.ax.set_title(title, fontsize=titleSize)

    def savePlotState(self):
        return self.settingsWindow.plotChanged()

    def updateData(self):
        self.settingsWindow.setKeys(
            self.data.getDataframe().columns.values.tolist())
        self.settingsWindow.plotChanged()
