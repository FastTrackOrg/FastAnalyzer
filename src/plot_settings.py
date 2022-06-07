from PySide2.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow
from PySide2.QtCore import Signal, QFile, QStandardPaths, Qt, QTimer
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_plot_settings import Ui_PlotSettings


class PlotSettings(QWidget):

    redraw = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_PlotSettings()
        self.ui.setupUi(self)

        self.ui.xLabel.editingFinished.connect(self.plotChanged)
        self.ui.yLabel.editingFinished.connect(self.plotChanged)
        self.ui.labelSize.valueChanged.connect(self.plotChanged)

        self.ui.title.editingFinished.connect(self.plotChanged)
        self.ui.titleSize.valueChanged.connect(self.plotChanged)

        self.ui.plotComboBox.currentIndexChanged.connect(self.plotChanged)
        self.ui.plotComboBox.currentTextChanged.connect(self.autoLabel)
        self.ui.keyComboBox.currentIndexChanged.connect(self.plotChanged)
        self.ui.idComboBox.currentIndexChanged.connect(self.plotChanged)
        self.ui.idComboBox.currentTextChanged.connect(self.customId)
        self.ui.idCustom.editingFinished.connect(self.plotChanged)

    def plotChanged(self):
        params = dict()
        params["xLabel"] = self.ui.xLabel.text()
        params["yLabel"] = self.ui.yLabel.text()
        params["labelSize"] = self.ui.labelSize.value()
        params["title"] = self.ui.title.text()
        params["titleSize"] = self.ui.titleSize.value()
        params["plotType"] = self.ui.plotComboBox.currentText()
        params["plotKey"] = self.ui.keyComboBox.currentText()
        params["idPlot"] = self.ui.idComboBox.currentText()
        params["idCustom"] = self.ui.idCustom.text()
        self.redraw.emit(params)

    def customId(self, text):
        if text == "Custom List":
            self.ui.idCustom.setEnabled(True)
        else:
            self.ui.idCustom.setEnabled(False)

    def autoLabel(self, text):
        if text == "histplot":
            yLabel = "Count"
        elif text == "kdeplot":
            yLabel = "Density"
        self.ui.yLabel.setText(yLabel)
        self.ui.xLabel.setText("px")
