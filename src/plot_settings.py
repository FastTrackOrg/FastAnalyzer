from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide2.QtCore import Signal, QFile, QStandardPaths, Qt, QTimer
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_plot_settings import Ui_PlotSettings


class PlotSettings(QWidget):

    redraw = Signal(dict)

    def __init__(self, parent=None, params=None):
        super().__init__(parent)
        self.ui = Ui_PlotSettings()
        self.ui.setupUi(self)

        if params:
            self.setValues(params)

        self.ui.xLabel.editingFinished.connect(self.plotChanged)
        self.ui.yLabel.editingFinished.connect(self.plotChanged)
        self.ui.labelSize.valueChanged.connect(self.plotChanged)

        self.ui.title.editingFinished.connect(self.plotChanged)
        self.ui.titleSize.valueChanged.connect(self.plotChanged)

        self.ui.plotType.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotType.currentTextChanged.connect(self.autoLabel)
        self.ui.plotKey.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotId.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotId.currentTextChanged.connect(self.customId)
        self.ui.customId.editingFinished.connect(self.plotChanged)

    def setValues(self, params):
        self.ui.xLabel.setText(params["xLabel"])
        self.ui.yLabel.setText(params["yLabel"])
        self.ui.labelSize.setValue(params["labelSize"])
        self.ui.title.setText(params["title"])
        self.ui.titleSize.setValue(params["titleSize"])
        self.ui.plotType.setCurrentText(params["plotType"])
        self.ui.plotKey.setCurrentText(params["plotKey"])
        self.ui.plotId.setCurrentText(params["plotId"])
        self.ui.customId.setText(params["customId"])

    def plotChanged(self):
        params = dict()
        params["xLabel"] = self.ui.xLabel.text()
        params["yLabel"] = self.ui.yLabel.text()
        params["labelSize"] = self.ui.labelSize.value()
        params["title"] = self.ui.title.text()
        params["titleSize"] = self.ui.titleSize.value()
        params["plotType"] = self.ui.plotType.currentText()
        params["plotKey"] = self.ui.plotKey.currentText()
        params["plotId"] = self.ui.plotId.currentText()
        params["customId"] = self.ui.customId.text()
        self.redraw.emit(params)
        return params

    def customId(self, text):
        if text == "Custom List":
            self.ui.customId.setEnabled(True)
        else:
            self.ui.customId.setEnabled(False)

    def autoLabel(self, text):
        if text == "histplot":
            yLabel = "Count"
        elif text == "kdeplot":
            yLabel = "Density"
        self.ui.yLabel.setText(yLabel)
        self.ui.xLabel.setText("px")
