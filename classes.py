from pandas import read_csv
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from numpy import std
from docx import Document
from docx.shared import Inches
from docx2pdf import convert
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.exporters


# import uuid


class graph:
    def __init__(self, graphPointer, window, buttons, numberOfGrapph):
        self.graphPointer = graphPointer
        self.numberOfGraph = numberOfGrapph
        self.window = window
        self.speedOfGraph = 1
        self.plottingPoint = 0
        self.imgNumber = 0
        self.graphPointer.addLegend(labelTextSize='9pt')
        self.handle_buttons(buttons)
        self.yAxisMaxOfSignals = []
        self.yAxisMinOfSignals = []
        self.snapshotsPaths = []
        self.snapshotStats = []
        self.signalDictionary = {}
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.speedOfGraph)
        self.timer.timeout.connect(self.plot)

    def handle_buttons(self, buttons):
        buttons[0].clicked.connect(self.add_signal)
        buttons[1].clicked.connect(self.pause_play_graph)
        buttons[2].clicked.connect(self.zoomIn)
        buttons[3].clicked.connect(self.zoomOut)
        buttons[4].clicked.connect(self.reset_graph)
        buttons[5].clicked.connect(self.clear_graph)
        buttons[6].clicked.connect(self.snap_shot_of_graph)
        buttons[7].clicked.connect(self.show_hide)
        buttons[8].clicked.connect(self.add_title)
        buttons[9].clicked.connect(self.delete_signal)
        buttons[10].clicked.connect(self.graph_speed_up)
        buttons[11].clicked.connect(self.graph_speed_down)
        buttons[12].clicked.connect(self.sync)
        buttons[13].clicked.connect(self.change_signal_color)
        self.signalComboBox = buttons[14]
        self.colorComboBox = buttons[15]
        self.colorComboBox.addItem("Red")
        self.colorComboBox.addItem("Green")
        self.colorComboBox.addItem("Blue")
        self.colorComboBox.addItem("Brown")
        self.colorComboBox.addItem("Pink")

    def add_signal(self):
        if self.timer.isActive():
            self.timer.stop()
        fileIfno = QFileDialog.getOpenFileName(self.window, "open csv file", "C:/Users/dell/Desktop/Old versions/graph",
                                               "CSV Files (*.csv)")
        if fileIfno[0] != '':
            filePath = fileIfno[0]
            # idOfNewSignal = uuid.uuid4()
            signalTitle = filePath.split("/")[-1][:-4]
            while signalTitle in self.signalDictionary.keys():
                numberOfTheSignal = 0
                signalTitle += " " + str(numberOfTheSignal)
            self.signalDictionary[signalTitle] = signals(
                filePath, signalTitle, self.graphPointer, self.window, self)
            self.signalComboBox.addItem(signalTitle)
            self.set_y_axis_range()
        else:
            QMessageBox.warning(self.window, "Error", "failed to add signal")
        self.timer.start()

    def pause_play_graph(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def plot(self):
        self.set_x_range()
        for signalToPlot in self.signalDictionary.values():
            if signalToPlot.signalStatus[0] == 'shown' and signalToPlot.signalStatus[1] == 'unfinished':
                signalToPlot.plotting_signal_curve(self.plottingPoint)
        self.plottingPoint += 1
        # QApplication.processEvents()

    def reset_graph(self):
        self.plottingPoint = 0
        if not self.timer.isActive():
            self.timer.start()

    def clear_graph(self):
        self.timer.stop()
        self.plottingPoint = 0
        self.graphPointer.clear()

    def graph_speed_up(self):
        if self.speedOfGraph > 5:
            self.speedOfGraph -= 5
            self.timer.setInterval(self.speedOfGraph)

        else:
            QMessageBox.information(
                self.window, "max speed", "this is the max speed")

    def graph_speed_down(self):
        self.speedOfGraph += 5
        self.timer.setInterval(self.speedOfGraph)

    def set_y_axis_range(self):
        yMin, yMax = min(self.yAxisMinOfSignals), max(self.yAxisMaxOfSignals)
        self.graphPointer.setYRange(yMin, yMax, padding=0)
        self.graphPointer.setLimits(yMin=2 * yMin, yMax=2 * yMax)

    def set_x_range(self):
        if len(self.signalDictionary) > 0:
            timeSpent = 0
            for signalToPlot in self.signalDictionary.values():
                timeSpent = self.plottingPoint * \
                    list(signalToPlot.values[0].values())[1]
                break
            if (timeSpent >= 2.8):
                self.graphPointer.setXRange(
                    timeSpent - 2.8, timeSpent + 0.1, padding=0)
            else:
                self.graphPointer.setXRange(0, 3, padding=0)
        else:
            self.graphPointer.setXRange(0, 3, padding=0)
        # QApplication.processEvents()

    def show_hide(self):
        self.signalDictionary[self.signalComboBox.currentText()
                              ].show_hide_signal()

    def add_title(self):
        pass

    def change_signal_color(self):
        chosenSignal = self.signalDictionary[self.signalComboBox.currentText()]
        chosenSignal.change_color(self.colorComboBox.currentText())
        chosenSignal.plotting_signal_curve(self.plottingPoint)

    def delete_signal(self):
        pass

    def zoomIn(self, active=False):
        pass

    def zoomOut(self, active=False):
        pass

    def snap_shot_of_graph(self):
        exporter = pyqtgraph.exporters.ImageExporter(self.graphPointer.scene())
        if self.numberOfGraph == 1:
            exporter.export(f"temp/imgs/graphOne/{self.imgNumber}.png")
            self.snapshotsPaths.append(
                f"temp/imgs/graphOne/{self.imgNumber}.png")
            QMessageBox.information(
                self.window, "saved", "your snapshot has been saved")

            boundaries = self.graphPointer.viewRange()  # to get the boundaries of the graph
            xmin, xmax = boundaries[0][0], boundaries[0][1]
            list_for_stat = [[], []]
            self.snapshotStats.append({})
            for signalToPlot in self.signalDictionary.values():
                if signalToPlot.signalStatus[0] == 'shown' and xmin < list(signalToPlot.values[0].values())[-1]:
                    for xPoint, yPoint in zip(list(signalToPlot.values[0].values()),
                                              list(signalToPlot.values[1].values())):
                        if xPoint > xmin:
                            list_for_stat[0].append(xPoint)
                            list_for_stat[1].append(yPoint)
                        if xPoint > xmax:
                            break

                    stats = [max(list_for_stat[1]), min(list_for_stat[1]), round(std((list_for_stat[1])), 4),
                             round(
                                 sum((list_for_stat[1])) / len((list_for_stat[1])), 4),
                             round(list_for_stat[0][-1] - (list_for_stat[0][0]), 4)]

                    list_for_stat[0].clear()
                    list_for_stat[1].clear()
                    last_added_signal = self.snapshotStats[-1]
                    last_added_signal[signalToPlot.title] = stats

        elif self.numberOfGraph == 2:
            exporter.export(f"temp/imgs/graphTwo/{self.imgNumber}.png")
            self.snapshotsPaths.append(
                f"temp/imgs/graphTwo/{self.imgNumber}.png")
            QMessageBox.information(
                self.window, "saved", "your snapshot has been saved")
            boundaries = self.graphPointer.viewRange()  # to get the boundaries of the graph
            xmin, xmax = boundaries[0][0], boundaries[0][1]
            list_for_stat = [[], []]
            self.snapshotStats.append({})
            for signalToPlot in self.signalDictionary.values():
                if signalToPlot.signalStatus[0] == 'shown' and xmin < list(signalToPlot.values[0].values())[-1]:
                    for xPoint, yPoint in zip(list(signalToPlot.values[0].values()),
                                              list(signalToPlot.values[1].values())):
                        if xPoint > xmin:
                            list_for_stat[0].append(xPoint)
                            list_for_stat[1].append(yPoint)
                        if xPoint > xmax:
                            break

                    stats = [max(list_for_stat[1]), min(list_for_stat[1]), round(std((list_for_stat[1])), 4),
                             round(
                                 sum((list_for_stat[1])) / len((list_for_stat[1])), 4),
                             round(list_for_stat[0][-1] - (list_for_stat[0][0]), 4)]

                    list_for_stat[0].clear()
                    list_for_stat[1].clear()
                    last_added_signal = self.snapshotStats[-1]
                    last_added_signal[signalToPlot.title] = stats

        self.imgNumber += 1

    def sync(self):
        pass


# ------------------------------------------signal class-------------------------------------------------------------------#

class signals(object):
    def __init__(self, filePath, signalTitle, graphPointer, window, graphObjectPoint):
        self.title = signalTitle
        self.color = "r"
        self.signalStatus = ['shown', 'unfinished']
        self.signalCurve = pg.PlotDataItem(name=self.title)
        self.window = window
        self.graphPointer = graphPointer
        self.graphPointer.addItem(self.signalCurve)
        data = read_csv(filePath)
        self.graphObjectPoint = graphObjectPoint
        self.startPoint = graphObjectPoint.plottingPoint
        if self.startPoint != 0:
            xColumn = data.columns.values.tolist()[0]
            for firstSignal in self.graphObjectPoint.signalDictionary.values():
                timeSpent = self.graphObjectPoint.plottingPoint * \
                    list(firstSignal.values[0].values())[1]
                break
            data[xColumn] = data[xColumn] + timeSpent
        dict_data = data.to_dict()
        # self.drownBefore = False
        self.values = list(dict_data.values())
        self.graphObjectPoint.yAxisMaxOfSignals.append(
            max(list(self.values[1].values())))
        self.graphObjectPoint.yAxisMinOfSignals.append(
            min(list(self.values[1].values())))
        self.graphObjectPoint.set_y_axis_range()
        self.stats = []
        self.calc_stats()

    def change_color(self, newColor):
        self.color = newColor

    def add_title(self):
        self.title = self.window.addTitle_lineEdit.text()
        self.signalCurve.setData(name=self.title)

    def show_hide_signal(self):
        if self.signalStatus[0] == 'hidden':
            self.graphPointer.addItem(self.signalCurve)
            self.signalStatus[0] = "shown"
        elif self.signalStatus[0] == 'shown':
            self.signalStatus[0] = 'hidden'
            self.graphPointer.removeItem(self.signalCurve)

    def check_status(self, plottingPoint):
        if (plottingPoint - self.startPoint) >= len(self.values[0].values()) - 1:
            return False
        else:
            return True

    def plotting_signal_curve(self, plottingPoint):
        if self.check_status(plottingPoint):
            self.signalCurve.setData(list(self.values[0].values())[:plottingPoint - self.startPoint],
                                     list(self.values[1].values())[
                :plottingPoint - self.startPoint],
                pen=self.color)
        else:
            self.signalCurve.setData(list(self.values[0].values()),
                                     list(self.values[1].values()),
                                     pen=self.color)
            self.signalStatus[1] = 'finished'

    def calc_stats(self):
        x_values = list(self.values[0].values())
        y_values = list(self.values[1].values())
        self.stats.append(max(y_values))
        self.stats.append(min(y_values))
        self.stats.append(round(std(y_values), 4))
        self.stats.append(round(sum(y_values) / len(y_values), 4))
        self.stats.append(round(x_values[-1] - x_values[0]))

    def setColor(self):
        pass

    def __del__(self):
        pass
