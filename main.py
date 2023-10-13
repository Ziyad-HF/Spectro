from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QInputDialog
from PyQt5.uic import loadUiType
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
from pandas import *
from classes import *
import sys
import pyqtgraph.exporters
from os import listdir, path, remove

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "mainWindow.ui"))


class MainApp(QMainWindow, FORM_CLASS):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self, parent=None)
        self.setupUi(self)
        self.graphicsView.setLimits(xMin=0)
        self.graphicsView2.setLimits(xMin=0)
        self.setWindowTitle("Spectro")
        self.setWindowIcon(QtGui.QIcon('icons/logo.ico'))
        # creating the first graph
        self.graphOne = graph(self.graphicsView, self, [self.addSignalBtn, self.pausePlayBtn,
                                                        self.zoomInBtn, self.zoomOutBtn,
                                                        self.resetBtn, self.clearBtn,
                                                        self.snapshotBtn, self.showHideBtn,
                                                        self.addTitleBtn, self.deleteSignalBtn,
                                                        self.speedUpBtn, self.speedDownBtn,
                                                        self.syncUnsyncSignalsBtn, self.addColorBtn,
                                                        self.signalComboBox, self.colorComboBox], 1)
        # creating the second graph
        self.graphTwo = graph(self.graphicsView2, self, [self.addSignalBtn2, self.pausePlayBtn2,
                                                         self.zoomInBtn2, self.zoomOutBtn2,
                                                         self.resetBtn2, self.clearBtn2,
                                                         self.snapshotBtn2, self.showHideBtn2,
                                                         self.addTitleBtn2, self.deleteSignalBtn2,
                                                         self.speedUpBtn2, self.speedDownBtn2,
                                                         self.syncUnsyncSignalsBtn2, self.addColorBtn2,
                                                         self.signalComboBox2, self.colorComboBox2], 2)
        self.handle_buttons()

    def handle_buttons(self):
        self.actionGenerate_PDF.triggered.connect(self.export_to_pdf)
        # self.syncUnsyncSignalsBtn.clicked.connect(self.capture_screenshot_save)

    def clean(self):
        graphOneFolderPath = "temp/imgs/graphOne"
        graphTwoFolderPath = "temp/imgs/graphTwo"
        # List all files in the folder
        graphOnefiles = listdir(graphOneFolderPath)
        graphTwofiles = listdir(graphTwoFolderPath)

        for file in graphOnefiles:
            file_path = path.join(graphOneFolderPath, file)
            # Check if the path is a file (not a subdirectory)
            if path.isfile(file_path):
                remove(file_path)
        for file in graphTwofiles:
            file_path = path.join(graphTwoFolderPath, file)
            # Check if the path is a file (not a subdirectory)
            if path.isfile(file_path):
                remove(file_path)  # Delete the file

        self.graphOne.snapshotsPaths.clear()
        self.graphOne.imageNumber = 0
        self.graphTwo.snapshotsPaths.clear()
        self.graphTwo.imageNumber = 0
        QApplication.processEvents() 

    def create_word(self):
        doc = Document()
        signalDictGraphOne = self.graphOne.signalDictionary
        signalDictGraphTwo = self.graphTwo.signalDictionary
        graphOneSignals = list(signalDictGraphOne.values())
        graphTwoSignals = list(signalDictGraphTwo.values())
        doc.add_heading("Report of statistics and Snapshots", 0)
        doc.add_paragraph("")

        doc.add_heading('General statistics on signals', 1)
        doc.add_paragraph("")

        # Define the number of rows and columns for the table
        num_rows = len(graphOneSignals) + \
            len(graphTwoSignals) + 1  # number of signal
        num_cols = 6
        # Add a table with the specified number of rows and columns
        table = doc.add_table(rows=num_rows, cols=num_cols)
        # Set the style of the table
        table.style = 'Light Shading'
        # Define table headings
        headings = ['Signal', 'Max', 'Min', 'Mean', 'STD', 'Duration']

        # Populate the first row of the table with headings
        for i, heading in enumerate(headings):
            cell = table.cell(0, i)
            cell.text = heading
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = cell.paragraphs[0].runs[0]
            run.bold = True
            run.font.size = Pt(12)

        # Add signals stats numbers
        data = []
        for signal in graphOneSignals:
            data.append([signal.title] + signal.stats)

        for signal in graphTwoSignals:
            data.append([signal.title] + signal.stats)

        for i, row_data in enumerate(data):
            for j, text in enumerate(row_data):
                cell = table.cell(i + 1, j)
                cell.text = str(text)
                cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                cell.width = Inches(2.0)
                cell.height = Inches(1.0)

        doc.add_paragraph("")
        if len(self.graphOne.snapshotsPaths) or len(self.graphTwo.snapshotsPaths) != 0:
            doc.add_heading("Here are Each snapshot and its statistics:\n")
        number = 1
        self.addSnapShotsToReport(
            self.graphOne.snapshotsPaths, self.graphOne.snapshotStats, doc, number)
        self.addSnapShotsToReport(
            self.graphTwo.snapshotsPaths, self.graphTwo.snapshotStats, doc, number)

        report_name, ok = QInputDialog.getText(
            self, 'Name your report', 'Enter Report Name:')

        report_path = None
        if ok:
            report_path = f"outputs/{report_name}"
        else:
            report_path = "outputs/report"

        while path.exists(path.join(report_path+".pdf")):
            report_path += "_"
            report_name += "_"

        doc.save(f"outputs/{report_name}.docx")

        QApplication.processEvents()

    def addSnapShotsToReport(self, paths, snapshotsSignals, doc, number):
        if len(paths) != 0:
            # for loop to print graph two images
            for imgPath, snapshotSignals in zip(paths, snapshotsSignals):
                doc.add_paragraph("\n")
                doc.add_heading(f"Snapshot {number}", 2)
                number += 1
                img = Image.open(imgPath)
                width, height = img.size
                doc.paragraphs[-1].add_run().add_picture(imgPath, width=Inches(width / 140),
                                                         height=Inches(height / 100))
                doc.add_paragraph("Snapshot Statistics")
                num_rows = 1 + len(snapshotSignals.keys())
                num_cols = 6
                table = doc.add_table(rows=num_rows, cols=num_cols)
                table.style = 'Light Shading'
                headings = ['Signal', 'Max', 'Min', 'Mean', 'STD', 'Duration']
                for i, heading in enumerate(headings):
                    cell = table.cell(0, i)
                    cell.text = heading
                    cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    run = cell.paragraphs[0].runs[0]
                    run.bold = True
                    run.font.size = Pt(12)

                rowIndex = 1
                for signal in snapshotSignals.items():
                    signalTitle, signalStats = signal
                    data = [signalTitle]
                    data.extend(signalStats)
                    for col, text in enumerate(data):
                        cell = table.cell(rowIndex, col)
                        cell.text = str(text)
                        cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        cell.width = Inches(2.0)
                        cell.height = Inches(1.0)
                    rowIndex += 1

    def export_to_pdf(self):
        self.create_word()
        self.clean()
        # Converting word files to PDFs
        convert("outputs/")
        QMessageBox.information(
            self, "Saved", "You will find your report in the outputs")

        for file in listdir("outputs/"):
            file_path = path.join("outputs/", file)

            # Check if the path is a file (not a subdirectory)
            if path.isfile(file_path) and file_path[-5:] == ".docx":
                remove(file_path)
        QApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
