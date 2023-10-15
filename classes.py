from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.exporters
from pandas import read_csv
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
import pyqtgraph as pg
from numpy import std


# import uuid


class Graph:
    def __init__(self, graph_pointer, window, buttons, number_of_graph):
        self.linkStatus = False
        self.playing = True
        self.graphPointer = graph_pointer
        self.numberOfGraph = number_of_graph
        self.window = window
        self.speedOfGraph = 21
        self.plottingPoint = 0
        self.imgNumber = 0
        self.graphPointer.addLegend(labelTextSize='9pt')
        self.buttons = buttons
        self.yAxisMaxOfSignals = []
        self.yAxisMinOfSignals = []
        # self.firstValuesOfTime= []
        self.snapshotsPaths = []
        self.snapshotStats = []
        self.signalDictionary = {}
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.speedOfGraph)
        self.timer.timeout.connect(self.plot)
        self.buttons[10].setEnabled(False)
        self.handle_buttons()

        self.syncStatus = False  # False for unsync True for sync
        self.zoom_factor = 1.0
        self.disable_enable_buttons()
        self.buttons[0].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/add.png")))
        self.buttons[1].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/pause.png")))
        self.buttons[4].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/reset.png")))
        self.buttons[5].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/clear.png")))
        self.buttons[6].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/snapshot.png")))
        self.buttons[7].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/hide.png")))
        self.buttons[10].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/speed up.png")))
        self.buttons[11].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/slow down.png")))
        self.buttons[16].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/original view.png")))
        self.buttons[17].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/default.png")))
        self.buttons[12].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/sync.png")))

    def disable_enable_buttons(self):
        if self.signalDictionary:
            for i in range(len(self.buttons)):
                if i != 0 and i != 18:
                    self.buttons[i].setEnabled(True)

        else:
            for i in range(len(self.buttons)):
                if i != 0 and i != 18:
                    self.buttons[i].setEnabled(False)

    def handle_buttons(self):
        self.check_speed_in_range()
        self.buttons[0].clicked.connect(self.add_signal)
        self.buttons[1].clicked.connect(self.pause_play_graph)
        self.buttons[2].clicked.connect(self.zoom_in)
        self.buttons[3].clicked.connect(self.zoom_out)
        self.buttons[4].clicked.connect(self.reset_graph)
        self.buttons[5].clicked.connect(self.clear_graph)
        self.buttons[6].clicked.connect(self.snap_shot_of_graph)
        self.buttons[7].clicked.connect(self.show_hide)
        self.buttons[8].clicked.connect(self.add_title)
        self.buttons[9].clicked.connect(self.delete_signal)
        self.buttons[10].clicked.connect(self.graph_speed_up)
        self.buttons[11].clicked.connect(self.graph_speed_down)
        self.buttons[12].clicked.connect(self.sync)
        self.buttons[16].clicked.connect(self.reset_original_view)
        # self.buttons[17].clicked.connect(self.move_signal_to_other_graph)
        self.buttons[14].currentIndexChanged.connect(self.change_signal_color)
        self.buttons[14].addItem("Red")
        self.buttons[14].addItem("Green")
        self.buttons[14].addItem("Blue")
        self.buttons[14].addItem("Brown")
        self.buttons[14].addItem("Pink")
        self.buttons[17].clicked.connect(self.default_speed)
        # QApplication.processEvents()

    def add_signal(self, file_path="", signal_title=""):

        if self.timer.isActive():
            self.timer.stop()
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self.window, "open csv file",
                                                       "data/",
                                                       "CSV Files (*.csv)")
            if file_path != '':
                signal_title = file_path.split("/")[-1][:-4]
                number_of_the_signal = 0
                while signal_title in self.signalDictionary.keys():
                    signal_title += " " + str(number_of_the_signal)
                    number_of_the_signal += 1
                self.signalDictionary[signal_title] = Signal(file_path, signal_title, self.graphPointer, self.window,
                                                             self)
                self.buttons[13].addItem(signal_title)
                self.set_y_axis_range()
                self.disable_enable_buttons()
                self.buttons[18].setEnabled(True)
                if self.linkStatus:
                    self.signalDictionary[signal_title].sync_signal(True)

            else:
                QMessageBox.warning(self.window, "Error", "failed to add signal")
            if not self.linkStatus:
                self.timer.start()
        else:
            number_of_the_signal = 0
            while signal_title in self.signalDictionary.keys():
                signal_title += " " + str(number_of_the_signal)
                number_of_the_signal += 1
            self.signalDictionary[signal_title] = Signal(file_path, signal_title, self.graphPointer, self.window, self)
            self.buttons[13].addItem(signal_title)
            self.set_y_axis_range()
            self.disable_enable_buttons()
            if self.linkStatus:
                self.signalDictionary[signal_title].sync_signal(True)
            if not self.linkStatus:
                self.timer.start()
            self.buttons[18].setEnabled(True)
        # QApplication.processEvents()

    def pause_play_graph(self):
        if self.playing:
            self.playing = False
            self.buttons[1].setText("Play")
            self.buttons[1].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/play.png")))
        else:
            self.playing = True
            self.buttons[1].setText("Pause")
            self.buttons[1].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/pause.png")))

        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()
        # QApplication.processEvents()

    def plot(self):
        self.set_x_range()
        i = 0
        for signalToPlot in self.signalDictionary.keys():
            if self.signalDictionary[signalToPlot].signalStatus[0] == 'shown' and \
                    self.signalDictionary[signalToPlot].signalStatus[1] == 'unfinished':
                self.signalDictionary[signalToPlot].plotting_signal_curve(self.plottingPoint)
                i += 1

        self.plottingPoint += 1
        QApplication.processEvents()

    def reset_graph(self):
        self.plottingPoint = 0
        if not self.timer.isActive() and not self.linkStatus:
            self.timer.start()
        # QApplication.processEvents()

    def clear_graph(self):
        self.timer.stop()
        self.plottingPoint = 0
        self.buttons[13].clear()
        self.graphPointer.clear()
        self.signalDictionary.clear()

    def check_speed_in_range(self):
        if self.speedOfGraph > 5:
            self.buttons[10].setEnabled(True)
        else:
            self.buttons[10].setEnabled(False)

        if self.speedOfGraph < 100:
            self.buttons[11].setEnabled(True)
        else:
            self.buttons[11].setEnabled(False)

    def graph_speed_up(self):
        self.speedOfGraph -= 5
        self.timer.setInterval(self.speedOfGraph)
        self.check_speed_in_range()

    def graph_speed_down(self):
        self.speedOfGraph += 5
        self.timer.setInterval(self.speedOfGraph)
        self.check_speed_in_range()

    def default_speed(self):
        self.speedOfGraph = 21
        self.buttons[10].setEnabled(True)
        self.buttons[11].setEnabled(True)
        self.timer.setInterval(self.speedOfGraph)

    def set_y_axis_range(self):
        y_min, y_max = min(self.yAxisMinOfSignals), max(self.yAxisMaxOfSignals)
        self.graphPointer.setYRange(y_min, y_max, padding=0)
        self.graphPointer.setLimits(yMin=2 * y_min, yMax=2 * y_max)
        QApplication.processEvents()

    def set_x_range(self):
        if self.numberOfGraph == 1 or not self.linkStatus:
            if len(self.signalDictionary) > 0:
                time_spent = self.plottingPoint * 0.032

                if time_spent >= 2.8:
                    self.graphPointer.setXRange(time_spent - 2.8, time_spent + 0.1, padding=0)
                else:
                    self.graphPointer.setXRange(0, 3, padding=0)
            else:
                self.graphPointer.setXRange(0, 3, padding=0)
        QApplication.processEvents()

    def show_hide(self):
        self.signalDictionary[self.buttons[13].currentText()].show_hide_signal()
        QApplication.processEvents()

    def add_title(self):
        if self.buttons[15].text() == "":
            QMessageBox.warning(self.window, "Empty Filed", "please enter a title")
        else:
            timer_status = self.timer.isActive()
            if timer_status:
                self.timer.stop()
            number_of_the_signal = 0
            signal_new_title = self.buttons[15].text()
            signal_old_title = self.buttons[13].currentText()

            while signal_new_title in self.signalDictionary.keys():
                number_of_the_signal += 1
                signal_new_title += " " + str(number_of_the_signal)
            chosen_signal = self.signalDictionary[signal_old_title]
            chosen_signal.add_title(signal_new_title)
            self.signalDictionary[signal_new_title] = self.signalDictionary.pop(signal_old_title)
            self.buttons[13].addItem(signal_new_title)
            self.buttons[13].removeItem(self.buttons[13].currentIndex())

            for snapshot in self.snapshotStats:
                if signal_old_title in snapshot.keys():
                    snapshot[signal_new_title] = snapshot.pop(signal_old_title)
            # chosen_signal.plotting_signal_curve(self.plottingPoint)
            if timer_status:
                self.timer.start()
            self.buttons[15].setText("")

    def change_signal_color(self):
        chosen_color = self.buttons[14].currentText()
        chosen_signal = self.signalDictionary[self.buttons[13].currentText()]
        chosen_signal.change_color(chosen_color)
        # QApplication.processEvents()

    def delete_signal(self, move_flag=False):
        chosen_signal_key = self.buttons[13].currentText()
        if chosen_signal_key in self.signalDictionary:
            self.signalDictionary[chosen_signal_key].delete_signal_signals()
            self.set_x_range()
            index = self.buttons[13].findText(chosen_signal_key)
            del self.signalDictionary[chosen_signal_key]
            if not self.signalDictionary:
                self.plottingPoint = 0
                self.disable_enable_buttons()
                if len(self.snapshotStats):
                    self.buttons[18].setEnabled(False)

            if index != -1:
                self.buttons[13].removeItem(index)
                self.timer.stop()
            if not move_flag:
                QMessageBox.information(self.window, "Signal deleted",
                                        f"Signal {chosen_signal_key} deleted from the graph")
        else:
            pass
        if self.buttons[13].count() == 0:
            self.timer.stop()
        else:
            self.timer.start()
        QApplication.processEvents()

    def zoom_in(self):
        self.timer.stop()
        self.zoom_factor *= 2  # Increase the zoom factor
        self.graphPointer.plotItem.getViewBox().scaleBy((1 / 2, 1 / 2))

    def zoom_out(self):
        self.timer.stop()
        self.zoom_factor /= 2  # Decrease the zoom factor
        self.graphPointer.plotItem.getViewBox().scaleBy((2, 2))

    def reset_original_view(self):
        self.zoom_factor = 1.0
        y_min, y_max = min(self.yAxisMinOfSignals), max(self.yAxisMaxOfSignals)
        self.graphPointer.setYRange(y_min, y_max, padding=0)
        self.timer.start()
        self.buttons[1].setText("play")
        self.buttons[1].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/play.png")))

    def snap_shot_of_graph(self):
        exporter = pyqtgraph.exporters.ImageExporter(self.graphPointer.scene())
        if self.numberOfGraph == 1:
            exporter.export(f"temp/imgs/graphOne/{self.imgNumber}.png")
            self.snapshotsPaths.append(
                f"temp/imgs/graphOne/{self.imgNumber}.png")
            QMessageBox.information(self.window, "saved", "your snapshot has been saved")

            boundaries = self.graphPointer.viewRange()  # to get the boundaries of the graph
            x_min, x_max = boundaries[0][0], boundaries[0][1]
            list_for_stat = [[], []]
            self.snapshotStats.append({})
            for signalToPlot in self.signalDictionary.values():
                if signalToPlot.signalStatus[0] == 'shown' and x_min < list(signalToPlot.values[0].values())[-1]:
                    for xPoint, yPoint in zip(list(signalToPlot.values[0].values()),
                                              list(signalToPlot.values[1].values())):
                        if xPoint > x_min:
                            list_for_stat[0].append(xPoint)
                            list_for_stat[1].append(yPoint)
                        if xPoint > x_max:
                            break

                    stats = [max(list_for_stat[1]), min(list_for_stat[1]), round(std((list_for_stat[1])), 4),
                             round(sum((list_for_stat[1])) / len((list_for_stat[1])), 4),
                             round(list_for_stat[0][-1] - (list_for_stat[0][0]), 4)]

                    list_for_stat[0].clear()
                    list_for_stat[1].clear()
                    last_added_signal = self.snapshotStats[-1]
                    last_added_signal[signalToPlot.title] = stats

        elif self.numberOfGraph == 2:
            exporter.export(f"temp/imgs/graphTwo/{self.imgNumber}.png")
            self.snapshotsPaths.append(
                f"temp/imgs/graphTwo/{self.imgNumber}.png")
            QMessageBox.information(self.window, "saved", "your snapshot has been saved")
            boundaries = self.graphPointer.viewRange()  # to get the boundaries of the graph
            x_min, x_max = boundaries[0][0], boundaries[0][1]
            list_for_stat = [[], []]
            self.snapshotStats.append({})
            for signalToPlot in self.signalDictionary.values():
                if signalToPlot.signalStatus[0] == 'shown' and x_min < list(signalToPlot.values[0].values())[-1]:
                    for xPoint, yPoint in zip(list(signalToPlot.values[0].values()),
                                              list(signalToPlot.values[1].values())):
                        if xPoint > x_min:
                            list_for_stat[0].append(xPoint)
                            list_for_stat[1].append(yPoint)
                        if xPoint > x_max:
                            break

                    stats = [max(list_for_stat[1]), min(list_for_stat[1]), round(std((list_for_stat[1])), 4),
                             round(sum((list_for_stat[1])) / len((list_for_stat[1])), 4),
                             round(list_for_stat[0][-1] - (list_for_stat[0][0]), 4)]

                    list_for_stat[0].clear()
                    list_for_stat[1].clear()
                    last_added_signal = self.snapshotStats[-1]
                    last_added_signal[signalToPlot.title] = stats

        self.imgNumber += 1
        QApplication.processEvents()

    def link(self, link_status):
        self.linkStatus = link_status
        if self.linkStatus:
            if not self.syncStatus:
                for signalToPlot in self.signalDictionary.values():
                    if signalToPlot.signalStatus[0] == 'shown':
                        signalToPlot.sync_signal(not self.syncStatus)
                        signalToPlot.plotting_signal_curve(self.plottingPoint)
                self.syncStatus = not self.syncStatus
            self.buttons[0].clicked.disconnect(self.add_signal)
            self.buttons[1].clicked.disconnect(self.pause_play_graph)
            self.buttons[2].clicked.disconnect(self.zoom_in)
            self.buttons[3].clicked.disconnect(self.zoom_out)
            self.buttons[4].clicked.disconnect(self.reset_graph)
            self.buttons[10].clicked.disconnect(self.graph_speed_up)
            self.buttons[11].clicked.disconnect(self.graph_speed_down)
            self.buttons[17].clicked.disconnect(self.default_speed)
            self.buttons[12].clicked.connect(self.sync)
        else:
            self.handle_buttons()

    def sync(self):
        for signalToPlot in self.signalDictionary.values():
            if signalToPlot.signalStatus[0] == 'shown':
                signalToPlot.sync_signal(not self.syncStatus)
                signalToPlot.plotting_signal_curve(self.plottingPoint)
        self.syncStatus = not self.syncStatus


# ------------------------------------------signal
# class-------------------------------------------------------------------


class Signal(object):
    def __init__(self, file_path, signal_title, graph_pointer, window, graph_object_point):
        self.filePath = file_path
        self.title = signal_title
        self.color = "r"
        self.signalStatus = ['shown', 'unfinished', '']
        self.signalCurve = pg.PlotDataItem(name=self.title)
        self.window = window
        self.graphPointer = graph_pointer
        self.graphPointer.addItem(self.signalCurve)
        self.data = read_csv(file_path)
        self.graphObjectPoint = graph_object_point
        self.startPoint = self.graphObjectPoint.plottingPoint
        if self.startPoint != 0:
            self.signalStatus[2] = 'unsync'
            self.timeSpent = self.startPoint * 0.032
            x_column = self.data.columns.values.tolist()[0]
            self.data[x_column] = self.data[x_column] + self.timeSpent
            # self.signalStatus[2] = 'unsync'

        else:
            self.timeSpent = 0
            self.signalStatus[2] = 'sync'
        dict_data = self.data.to_dict()
        self.values = list(dict_data.values())
        self.graphObjectPoint.yAxisMaxOfSignals.append(max(list(self.values[1].values())))
        self.graphObjectPoint.yAxisMinOfSignals.append(min(list(self.values[1].values())))
        # self.graphObjectPoint.firstValuesOfTime.append((list(self.values[0].values())[1]))
        self.graphObjectPoint.set_y_axis_range()
        self.stats = []
        self.calc_stats()
        # QApplication.processEvents()

    def return_path(self):
        return self.filePath, self.title

    def sync_signal(self, sync_status):
        x_column = self.data.columns.values.tolist()[0]
        if self.signalStatus[2] == 'unsync':
            if sync_status:
                self.startPoint = 0
                self.data[x_column] = self.data[x_column] - self.timeSpent
                self.graphObjectPoint.buttons[12].setText("Unsync")
                self.graphObjectPoint.buttons[12].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/unsync.png")))

            else:
                self.startPoint = int((self.timeSpent / 0.032))
                self.data[x_column] = self.data[x_column] + self.timeSpent
                self.graphObjectPoint.buttons[12].setText("Sync")
                self.graphObjectPoint.buttons[12].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/sync.png")))
            dict_data = self.data.to_dict()
            self.values = list(dict_data.values())
            QApplication.processEvents()

    def change_color(self, new_color):
        self.color = new_color

    def add_title(self, newt_title):
        self.title = newt_title
        self.graphPointer.plotItem.legend.removeItem(self.signalCurve)
        self.graphPointer.plotItem.legend.addItem(self.signalCurve, self.title)

    def show_hide_signal(self):
        if self.signalStatus[0] == 'hidden':
            self.graphPointer.addItem(self.signalCurve)
            self.graphObjectPoint.buttons[7].setText("Hide")
            self.graphObjectPoint.buttons[7].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/hide.png")))
            self.signalStatus[0] = "shown"
        elif self.signalStatus[0] == 'shown':
            self.signalStatus[0] = 'hidden'
            self.graphObjectPoint.buttons[7].setText("Show")
            self.graphObjectPoint.buttons[7].setIcon(QtGui.QIcon(QtGui.QPixmap("icons/show.png")))
            self.graphPointer.removeItem(self.signalCurve)
        QApplication.processEvents()

    def check_status(self, plotting_point):
        if (plotting_point - self.startPoint) >= len(self.values[0].values()) - 1:
            return False
        else:
            return True

    def plotting_signal_curve(self, plotting_point):
        if self.check_status(plotting_point):
            self.signalCurve.setData(list(self.values[0].values())[:plotting_point - self.startPoint],
                                     list(self.values[1].values())[:plotting_point - self.startPoint],
                                     pen=self.color, name=self.title)
        else:
            self.signalCurve.setData(list(self.values[0].values()),
                                     list(self.values[1].values()),
                                     pen=self.color, name=self.title)
            self.signalStatus[1] = 'finished'
        QApplication.processEvents()

    def calc_stats(self):
        x_values = list(self.values[0].values())
        y_values = list(self.values[1].values())
        self.stats.append(max(y_values))
        self.stats.append(min(y_values))
        self.stats.append(round(std(y_values), 4))
        self.stats.append(round(sum(y_values) / len(y_values), 4))
        self.stats.append(round(x_values[-1] - x_values[0]))
        QApplication.processEvents()

    def delete_signal_signals(self):
        self.graphPointer.removeItem(self.signalCurve)
        self.graphObjectPoint.yAxisMaxOfSignals.remove(max(list(self.values[1].values())))
        self.graphObjectPoint.yAxisMinOfSignals.remove(min(list(self.values[1].values())))
        self.graphPointer.plotItem.legend.removeItem(self.signalCurve)
