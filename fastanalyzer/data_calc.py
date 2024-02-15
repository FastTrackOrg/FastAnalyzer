from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem, QWidget
from PySide6.QtCore import Signal, QFile, QCoreApplication, QStandardPaths, Qt, QTimer, QSignalBlocker
from PySide6.QtGui import QColor, QIcon, QPen, QPainter, QAction, QActionGroup, QPalette, QPixmap, QFont, QFontDatabase
import PySide6.QtXml
from ui_data_calc import Ui_DataCalc
import numpy as np


class DataCalc(QMainWindow):

    dataChanged = Signal()
    # self.redraw.emit(params)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.ui = Ui_DataCalc()
        self.ui.setupUi(self)
        self.ui.toolBar.addWidget(self.ui.label)
        self.ui.toolBar.addWidget(self.ui.custom)

        self.data = data
        self.operations = []
        self.data.getDataframe().sort_values(
            by=["id", "imageNumber"], inplace=True)

        if "xHead_meters" in self.data.getDataframe():
            self.ui.scale.setValue(
                (self.data.getDataframe()["xHead_meters"] /
                 self.data.getDataframe()["xHead"]).values[0])
        if "time_seconds" in self.data.getDataframe():
            self.ui.timeScale.setValue((self.data.getDataframe(
            )["time_seconds"] / self.data.getDataframe()["imageNumber"]).values[-1])

        for i in ["Head", "Body", "Tail"]:
            velocity = np.array([])
            # Select data for one id to compute by object values
            for j in set(self.data.getDataframe()["id"]):
                dat = self.data.getDataframe()[
                    self.data.getDataframe()["id"] == j]
                velocity = np.append(velocity, ((dat["x{}".format(i)].diff(
                )**2 + dat["y{}".format(i)].diff()**2).pow(0.5) / dat["t{}".format(i)].diff()).values)
            self.data.getDataframe()["velocity{}".format(i)] = velocity

        self.loadDataInTable()

        self.ui.table.itemChanged.connect(self.updateData)

        self.ui.custom.editingFinished.connect(self.addColumn)

        self.ui.scale.valueChanged.connect(self.setScale)
        self.ui.timeScale.valueChanged.connect(self.setScale)

    def loadDataInTable(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        blocker = QSignalBlocker(self.ui.table)
        blocker.reblock()
        self.ui.table.setRowCount(len(self.data.getDataframe()))
        self.ui.table.setColumnCount(len(self.data.getDataframe().columns))
        for i, j in enumerate(
                self.data.getDataframe().columns.values.tolist()):
            self.ui.table.setHorizontalHeaderItem(i, QTableWidgetItem(j))
        for col, __ in enumerate(self.data.getDataframe().columns):
            for row, val in enumerate(
                    self.data.getDataframe().iloc[:, col].values):
                self.ui.table.setItem(row, col, QTableWidgetItem(str(val)))
        QSignalBlocker(self.ui.table).unblock()
        QApplication.restoreOverrideCursor()

    def addColumn(self):
        if i := self.ui.custom.text():
            QApplication.setOverrideCursor(Qt.WaitCursor)
            blocker = QSignalBlocker(self.ui.table)
            blocker.reblock()
            try:
                self.data.getDataframe().eval(i, inplace=True)
                self.operations.append(i)
                self.ui.custom.setText(str())
                self.ui.statusbar.showMessage(QCoreApplication.translate(
                    "data_calc", "{} performed with success".format(i)))
                self.loadDataInTable()
                self.dataChanged.emit()
            except Exception as e:
                self.ui.statusbar.showMessage(str(e))
            blocker.unblock()
            QApplication.restoreOverrideCursor()

    def updateData(self, new):
        try:
            self.data.getDataframe().iat[new.row(),
                                         new.column()] = float(new.text())
        except BaseException:
            new.setText(
                str(self.data.getDataframe().iat[new.row(), new.column()]))

    def setScale(self):
        scale = self.ui.scale.value()
        timeScale = self.ui.timeScale.value()
        for i in ["Body", "Tail", "Head"]:
            self.data.getDataframe()[
                "x{}_meters".format(i)] = self.data.getDataframe()[
                "x{}".format(i)] * scale
            self.data.getDataframe()[
                "y{}_meters".format(i)] = self.data.getDataframe()[
                "y{}".format(i)] * scale
            self.data.getDataframe()["velocity{}_meters_by_second".format(
                i)] = self.data.getDataframe()["velocity{}".format(i)] * (scale / timeScale)
            self.data.getDataframe()[
                "{}MajorAxisLength_meters".format(
                    i.lower())] = self.data.getDataframe()[
                "{}MajorAxisLength".format(
                    i.lower())] * scale
            self.data.getDataframe()[
                "{}MinorAxisLength_meters".format(
                    i.lower())] = self.data.getDataframe()[
                "{}MinorAxisLength".format(
                    i.lower())] * scale
        self.data.getDataframe()["curvature_inverse_meters"] = self.data.getDataframe()[
            "curvature"] / scale
        self.data.getDataframe()["time_seconds"] = self.data.getDataframe()[
            "imageNumber"] * timeScale
        self.data.getDataframe()["areaBody_meters_square"] = self.data.getDataframe()[
            "areaBody"] * scale**2
        self.data.getDataframe()["perimeterBody_meters"] = self.data.getDataframe()[
            "perimeterBody"] * scale
        for i in self.operations:
            self.data.getDataframe().eval(i, inplace=True)
        self.loadDataInTable()
        self.dataChanged.emit()
