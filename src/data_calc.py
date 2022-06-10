from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QActionGroup, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem, QWidget
from PySide2.QtCore import Signal, QFile, QStandardPaths, Qt, QTimer, QSignalBlocker
from PySide2.QtGui import QColor, QIcon, QPen, QPainter, QPalette, QPixmap, QFont, QFontDatabase
import PySide2.QtXml
from ui_data_calc import Ui_DataCalc
import numpy as np


class DataCalc(QMainWindow):

    dataChanged = Signal()
    #self.redraw.emit(params)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.ui = Ui_DataCalc()
        self.ui.setupUi(self)


        self.data = data
        self.data.getDataframe().sort_values(by=["id", "imageNumber"], inplace=True)

        for i in ["Head", "Body", "Tail"]:
            velocity = np.array([])
            # Select data for one id to compute by object values
            for j in set(self.data.getDataframe()["id"]):
                dat = self.data.getDataframe()[self.data.getDataframe()["id"] == j]
                velocity = np.append(velocity, ((dat["x{}".format(i)].diff()**2 + dat["y{}".format(i)].diff()**2).pow(0.5) / dat["t{}".format(i)].diff()).values)
            self.data.getDataframe()["velocity{}".format(i)] = velocity

        self.loadDataInTable()

        self.ui.table.itemChanged.connect(self.updateData)

        self.ui.custom.editingFinished.connect(self.addColumn)
        self.ui.custom.editingFinished.connect(self.loadDataInTable)

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
                self.ui.custom.setText(str())
                self.ui.customDisplay.setText(str())
                self.dataChanged.emit()
            except Exception as e:
                self.ui.customDisplay.setText(str(e))
            blocker.unblock()
            QApplication.restoreOverrideCursor()

    def updateData(self, new):
        try:
            self.data.getDataframe().iat[new.row(), new.column()] = float(new.text())
        except:
            new.setText(str(self.data.getDataframe().iat[new.row(), new.column()]))
