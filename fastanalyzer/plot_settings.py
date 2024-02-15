from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide6.QtCore import Signal, QFile, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QAction, QPixmap, QFont, QFontDatabase
import PySide6.QtXml
from ui_plot_settings import Ui_PlotSettings


class PlotSettings(QWidget):

    redraw = Signal(dict)

    def __init__(self, parent=None, keys=None, params=None):
        super().__init__(parent)
        self.ui = Ui_PlotSettings()
        self.ui.setupUi(self)

        if keys:
            self.setKeys(keys)
        if params:
            self.setValues(params)

        self.ui.xLabel.editingFinished.connect(self.plotChanged)
        self.ui.yLabel.editingFinished.connect(self.plotChanged)
        self.ui.labelSize.valueChanged.connect(self.plotChanged)

        self.ui.title.editingFinished.connect(self.plotChanged)
        self.ui.titleSize.valueChanged.connect(self.plotChanged)

        self.ui.plotType.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotType.currentTextChanged.connect(self.setPlotType)

        self.ui.plotKey.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotKeyX.currentIndexChanged.connect(self.plotChanged)

        self.ui.plotId.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotId.currentTextChanged.connect(self.customId)

        self.ui.customId.editingFinished.connect(self.plotChanged)

        self.ui.lowLevelApi.editingFinished.connect(self.plotChanged)

        self.univariateDistPlot = ["histplot", "kdeplot"]
        self.statPlot = ["boxplot", "violinplot", "swarmplot", "boxenplot"]

        self.ui.pTest.currentIndexChanged.connect(self.plotChanged)
        self.ui.pPairs.editingFinished.connect(self.plotChanged)

        # Workaround to force redraw to setup automatically all the labels
        originalIndex = self.ui.plotType.currentIndex()
        self.ui.plotType.setCurrentIndex(0)
        self.ui.plotType.setCurrentIndex(originalIndex)
        originalIndex = self.ui.plotId.currentIndex()
        self.ui.plotId.setCurrentIndex(0)
        self.ui.plotId.setCurrentIndex(originalIndex)

    def setValues(self, params):
        self.ui.xLabel.setText(params["xLabel"])
        self.ui.yLabel.setText(params["yLabel"])
        self.ui.labelSize.setValue(params["labelSize"])
        self.ui.title.setText(params["title"])
        self.ui.titleSize.setValue(params["titleSize"])
        self.ui.plotType.setCurrentText(params["plotType"])
        self.ui.plotKey.setCurrentText(params["plotKey"])
        self.ui.plotKeyX.setCurrentText(params["plotKeyX"])
        self.ui.plotId.setCurrentText(params["plotId"])
        self.ui.customId.setText(params["customId"])
        self.ui.lowLevelApi.setText(params["lowLevelApi"])
        self.ui.pTest.setCurrentText(params["pTest"])
        self.ui.pPairs.setText(params["pPairs"])

    def plotChanged(self):
        self.autoLabel()
        params = dict()
        params["xLabel"] = self.ui.xLabel.text()
        params["yLabel"] = self.ui.yLabel.text()
        params["labelSize"] = self.ui.labelSize.value()
        params["title"] = self.ui.title.text()
        params["titleSize"] = self.ui.titleSize.value()
        params["plotType"] = self.ui.plotType.currentText()
        params["plotKey"] = self.ui.plotKey.currentText()
        params["plotKeyX"] = self.ui.plotKeyX.currentText()
        params["plotId"] = self.ui.plotId.currentText()
        params["customId"] = self.ui.customId.text()
        params["pTest"] = self.ui.pTest.currentText()
        params["pPairs"] = self.ui.pPairs.text()
        if not self.ui.lowLevelApi.text():
            self.ui.lowLevelApi.setText("{}")
        params["lowLevelApi"] = self.ui.lowLevelApi.text()
        self.redraw.emit(params)
        return params

    def customId(self, text):
        if text == "Custom List":
            self.ui.customId.setEnabled(True)
        else:
            self.ui.customId.setEnabled(False)

    def setPlotType(self, plotType):
        if plotType in self.univariateDistPlot:
            self.ui.plotKeyX.setEnabled(True)
            self.ui.x.setText("X")
            self.ui.y.setText("Y")
            self.ui.hue.setText("Cat")
            self.ui.pTest.setEnabled(False)
            self.ui.pPairs.setEnabled(False)
        elif plotType in self.statPlot:
            self.ui.plotKeyX.setEnabled(False)
            self.ui.x.setText("Y")
            self.ui.hue.setText("X")
            self.ui.pTest.setEnabled(True)
            self.ui.pPairs.setEnabled(True)

    def autoLabel(self):
        self.ui.pDetail.clear()
        if self.ui.plotType.currentText() in self.univariateDistPlot:
            xLabel = self.ui.plotKey.currentText()
            yLabel = self.ui.plotKeyX.currentText()
            if self.ui.plotKeyX.currentText(
            ) == "None" and self.ui.plotType.currentText() == "histplot":
                yLabel = "Count"
            elif self.ui.plotKey.currentText() == "None" and self.ui.plotType.currentText() == "histplot":
                xLabel = "Count"
            if self.ui.plotKeyX.currentText(
            ) == "None" and self.ui.plotType.currentText() == "kdeplot":
                yLabel = "Density"
            elif self.ui.plotKey.currentText() == "None" and self.ui.plotType.currentText() == "kdeplot":
                xLabel = "Density"
        elif self.ui.plotType.currentText() in self.statPlot:
            xLabel = "Id"
            yLabel = self.ui.plotKey.currentText()
        else:
            yLabel = str()
            yLabel = str()
        self.ui.yLabel.setText(yLabel)
        self.ui.xLabel.setText(xLabel)

    def setKeys(self, keys):
        keys.sort()
        prev = (self.ui.plotKey.currentText(), self.ui.plotKeyX.currentText())
        self.ui.plotKey.clear()
        self.ui.plotKey.addItems(keys + ["None"])
        self.ui.plotKeyX.clear()
        self.ui.plotKeyX.addItems(["None"] + keys)
        self.ui.plotKey.setCurrentText(prev[0])
        self.ui.plotKeyX.setCurrentText(prev[1])
