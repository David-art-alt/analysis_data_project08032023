# -*- coding :utf-8 -*-
'''This module provides views to manage the analysis data table'''
import csv
from openpyxl.workbook import Workbook
import os, sys, time, json
from collections import namedtuple
import pandas as pd


from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtGui import QFont, QPainter, QColor, QIcon, QPixmap
from PyQt6.QtCore import QDate, QTime, QDateTime, Qt, QTimer
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QPushButton,
    QTableView,
    QVBoxLayout, QDialog, QGridLayout, QComboBox, QLabel, QLineEdit, QGroupBox, QDoubleSpinBox, QFormLayout,
    QMessageBox, QDialogButtonBox, QFileDialog, QSplitter

)

from .model import AnalysisDataModel
from .database import createConnection
from .ultiproximate import df_oxygen_calc, df_wf_calc, df_waf_calc, oxygen_calc


class LoginGUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initialzeUI()

    def initialzeUI(self):
        self.setFixedSize(380, 260)
        self.setWindowTitle("Analysis Data Management")
        self.setupWindow()

    def setupWindow(self):
        """Set up the widgets for the login GUI"""
        # creating a label widget

        # setting label text
        headerLabel = QLabel("Analysis Data Management")
        headerLabel.setFont(QFont("Arial", 20))


        serverNameEntry = QLineEdit()
        serverNameEntry.setMinimumWidth(250)
        serverNameEntry.setText('localhost')

        self.userEntry = QLineEdit()
        self.userEntry.setMinimumWidth(250)

        self.passwordEntry = QLineEdit()
        self.passwordEntry.setMinimumWidth(250)
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)

        # Arrange the QLineEdit widgets into a QFormLayout
        loginForm = QFormLayout()
        loginForm.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        loginForm.addRow("Server Name:", serverNameEntry)
        loginForm.addRow("User Login:", self.userEntry)
        loginForm.addRow("Password:", self.passwordEntry)

        connectButton = QPushButton("Connect")
        connectButton.clicked.connect(self.connectToDatabase)

        newUserButton = QPushButton("No Account")
        newUserButton.clicked.connect(self.createNewUser)

        mainVbox = QVBoxLayout()
        mainVbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        mainVbox.addWidget(headerLabel,alignment= Qt.AlignmentFlag.AlignCenter)
        mainVbox.addSpacing(20)
        mainVbox.addLayout(loginForm)
        mainVbox.addSpacing(10)
        mainVbox.addWidget(connectButton)
        mainVbox.addWidget(newUserButton)
        self.setLayout(mainVbox)

    def connectToDatabase(self):
        """Check the user#s information. Close the login window if a match is found
        and open the SQL Mainwindow"""

        users = {}  # Create a new dictionary to store the user information

        with open('login.json', encoding='utf-8-sig') as json_f:
            loginData = json.load(json_f)

        # Load information from json file into a dictionary
        for login in loginData['loginlist']:
            user, pswd = login['username'], login['password']
            users[user] = pswd  # Set the dict's key and value pair

        # Collect information that the user entered
        userName = self.userEntry.text()
        password = self.passwordEntry.text()
        self.username = userName


        if (userName, password) in users.items():
            time.sleep(0.5)
            self.parent.search.setText(self.userEntry.text())
            self.parent.username = userName
            self.parent.show()
            self.close()
        else:
            QMessageBox.warning(self, "Information Incorrect",
                                "The user name or password is incorrect.", QMessageBox.StandardButton.Close)

    def toInputData (self):
        return self.userEntry.text()

    def createNewUser(self):
        """Set up the dialog box for the user to create a new user account."""
        self.hide()  # hide the login window
        self.newUserDialog = QDialog(self)
        self.newUserDialog.setWindowTitle("Create New User")

        headerLabel = QLabel("Create New User Account")
        headerLabel.setFont(QFont("Arial", 20))
        headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.newUserEntry = QLineEdit()
        self.newUserEntry.setMinimumWidth(250)
        self.newPassword = QLineEdit()
        self.newPassword.setMinimumWidth(250)
        self.newPassword.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirmPassword = QLineEdit()
        self.confirmPassword.setMinimumWidth(250)
        self.confirmPassword.setEchoMode(QLineEdit.EchoMode.Password)

        # Arrange QLineEdit widgets in a QFormLayout

        dialogForm = QFormLayout()
        dialogForm.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        dialogForm.addRow("New User Login:", self.newUserEntry)
        dialogForm.addRow("New Password:", self.newPassword)
        dialogForm.addRow("Confirm Password", self.confirmPassword)

        # Create sign up button

        createAcctButton = QPushButton("Create New Account")
        createAcctButton.clicked.connect(self.acceptUserInfo)

        dialogVbox = QVBoxLayout()
        dialogVbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        dialogVbox.addWidget(headerLabel)
        dialogVbox.addSpacing(20)
        dialogVbox.addLayout(dialogForm, 1)
        dialogVbox.addWidget(createAcctButton)
        self.newUserDialog.setLayout(dialogVbox)

        self.newUserDialog.show()

    def acceptUserInfo(self):

        userNameText = self.newUserEntry.text()
        passwordText = self.newPassword.text()
        confirmText = self.confirmPassword.text()

        if passwordText != confirmText:
            QMessageBox.warning(self, "Error Message",
                                "Entered Passwords do not match. Please Try again.",
                                QMessageBox.StandardButton.Close
                                )
        else:
            userInfo = {}

            with open('login.json', 'r+', encoding='utf-8-sig') as json_f:
                loginData = json.load(json_f)
                print(loginData)
                loginData['loginlist'].append({
                    "username": userNameText,
                    "password": passwordText
                })

                loginData.update(userInfo)
                json_f.seek(0)  # Reset the file pointer to position 0
                json.dump(loginData, json_f, indent=2)

        self.newUserDialog.close()
        self.show()





class MainWindow(QMainWindow):
    """Main Window"""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.initializeUI()

    def initializeUI(self):
        self.setWindowIcon(QIcon(QPixmap('IconIVET.png')))
        self.setWindowTitle("HTC Analysis and Process Data")
        self.setMinimumSize(1400, 550)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QGridLayout()
        self.centralWidget.setLayout(self.layout)

        self.login = LoginGUI(self)
        self.login.show()

        createConnection('analysisdata.sqlite')
        self.analysisDataModel = AnalysisDataModel()
        self.setupUI()

    def setupUI(self):
        """Setup the main window's GUI."""

        # Create the table view widget
        self.table = QTableView()
        self.table.setModel(self.analysisDataModel.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.resizeColumnsToContents()

        # Create Buttons
        self.addButton = QPushButton("Add...")
        self.addButton.clicked.connect(self.openAddDataDialog)
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.deleteData)
        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.exportAsCSV)
        self.exportXlsxButton = QPushButton("Export .xlsx")
        self.exportXlsxButton.clicked.connect(self.exportAsXlsx)
        self.plotButton = QPushButton("Plot")
        self.plotButton.clicked.connect(self.plotData)

        for button in (self.addButton, self.deleteButton, self.exportButton, self.exportXlsxButton, self.plotButton):
            button.setFixedWidth(150)

        #self.clearAllButton = QPushButton("Clear All")
        #self.clearAllButton.clicked.connect(self.clearAll)

        # Search Field
        self.search = QLineEdit()
        self.search.setFixedWidth(250)
        self.searchLabel = QLabel('Search User')
        self.search.textChanged.connect(self.updateFilter)

        # Time and Date
        self.dateLabel = QLabel()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showDatetime)
        self.timer.start(1000)

        font = QFont()
        font.setPointSize(15)
        self.search.setFont(font)
        self.searchLabel.setFont(font)

        topLayout = QFormLayout()
        topLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topLayout.addRow(self.searchLabel,self.search)


        # Layout for Buttons
        layout = QFormLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addRow(self.addButton)
        layout.addRow(self.deleteButton)
        layout.addRow(self.exportButton)
        layout.addRow(self.exportXlsxButton)
        layout.addRow(self.plotButton)


        self.layout.addLayout(topLayout,0,3,1,2)
        self.layout.addWidget(self.table, 1,0,1,7)
        self.layout.addLayout(layout, 1,7,1,1)
        self.layout.addWidget(self.dateLabel,2,7,1,1)




    def showDatetime(self):
        time = QDateTime.currentDateTime()
        timeDisplay = time.toString('yyyy-MM-dd  hh:mm:ss')
        self.dateLabel.setText(timeDisplay)



    def openAddDataDialog(self):
        """Open the Data Input dialog"""
        dialog = DataInputWindow(self)
        dialog.username = self.username
        print("openAddDataDialog")
        # print(QDialog.accepted)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("IF openAddDataDialog")
            self.analysisDataModel.addData(dialog.data)
            self.table.resizeColumnsToContents()

    def deleteData(self):
        row = self.table.currentIndex().row()

        if row < 0:
            return

        if self.analysisDataModel.model.record(row).value("name") != self.username:
            print("Yes")
            QMessageBox.information(
                self,
                "Warning!",
                "You can only delete your own data!",
                QMessageBox.StandardButton.Ok
            )

        else:
            messageBox = QMessageBox.warning(
                self,
                "Warning!",
                "Do you want tho remove the selceted data?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            if messageBox == QMessageBox.StandardButton.Ok:
                self.analysisDataModel.deleteData(row)

    '''
    def clearAll(self):
        """Remove all data from the database."""
        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want tho remove the selceted data?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        if messageBox == QMessageBox.StandardButton.Ok:
            self.analysisDataModel.clearAll()
    
    '''

    def exportAsXlsx(self):
        '''
        Exports data from selected rows as *.xlsx.
        '''

        indexes = self.table.selectionModel().selectedRows()
        headers = ["SampleID", "Process", "C_an [wt%]", "H_an [wt%]", "N_an [wt%]", "S_an [wt%]","Ash_an [wt%]",
             "Volatiles_an [wt%]", "Analysis moisture [wt%]", "Temperature [°C]", "Pressure [bar]", "Residence time [min]", "Additives", "lo Heating value_an [J/g]"]
        for index in indexes:
            print(index)
            print(self.table.model().data(self.table.model().index(index.row(), 1)))
        data = [headers]

        for index in indexes:
            rowData = []
            for col in range(2,self.analysisDataModel.model.columnCount()):
                field = self.table.model().data(self.table.model().index(index.row(), col))
                rowData.append(field)
            data.append(rowData)

        df_an = pd.DataFrame(data)
        df_an.columns = df_an.iloc[0]
        df_an = df_an[1:]


        print(df_an.to_markdown())
        df_an = df_oxygen_calc(df_an)


        """
        df_calc_oxy = df_an[["Analysis moisture [wt%]", "Ash_an [wt%]", "C_an [wt%]", "H_an [wt%]", "N_an [wt%]", "S_an [wt%]"]]

        # Oxygen by difference
        df_an["O_an [wt%]"] = 100 - df_calc_oxy.sum(axis=1)
        """

        cols = ["SampleID", "Temperature [°C]", "Pressure [bar]", "Residence time [min]", "Additives", "Process", "Analysis moisture [wt%]", "Ash_an [wt%]", "Volatiles_an [wt%]", "C_an [wt%]", "H_an [wt%]", "N_an [wt%]","O_an [wt%]", "S_an [wt%]",
               "lo Heating value_an [J/g]"]

        df_an = df_an[cols]



        """
        # Analysis Data to wf basis
        df_an_calc = df_an[["Ash_an [wt%]","Volatiles_an [wt%]","C_an [wt%]","H_an [wt%]","N_an [wt%]","S_an [wt%]","O_an [wt%]" ]]
        df_an["wf_base"] =(100 - df_an["Analysis moisture [wt%]"])/100
        df_an [["Ash_wf [wt%]","Volatiles_wf [wt%]","C_wf [wt%]","H_wf [wt%]","N_wf [wt%]","S_wf [wt%]","O_wf [wt%]"]] = df_an_calc.div(df_an["wf_base"],axis = 0)
        df_an_wf = df_an
        """
        df_an_wf = df_wf_calc(df_an)
        """
        # Analysis Data to waf basis
        df_an_wf_calc = df_an_wf [["Volatiles_wf [wt%]","C_wf [wt%]","H_wf [wt%]","N_wf [wt%]","S_wf [wt%]","O_wf [wt%]"]]
        df_an_wf["waf_base"] = (100 - df_an_wf["Ash_wf [wt%]"]) / 100
        df_an_wf[["Volatiles_waf [wt%]", "C_waf [wt%]", "H_waf [wt%]", "N_waf [wt%]", "S_waf [wt%]", "O_waf [wt%]"]] = df_an_wf_calc.div(df_an_wf["waf_base"], axis=0)
        df_an_wf_waf = df_an_wf"""
        df_an_wf_waf = df_waf_calc(df_an_wf)
        print(df_an_wf_waf.to_markdown())

        file_filter = 'Data File (*.xlsx)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Select a data file',
            directory='*.xlsx',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)'
        )
        # filepath is the first object of the respone tuple
        filepath = response[0]
        print(response)
        with pd.ExcelWriter(filepath) as writer:
            df_an_wf_waf.to_excel(writer, sheet_name='Sheet_name_1')
        #df.to_excel(filepath)


    def exportAsCSV(self):
        #response filepath and filte to save *.csv
        file_filter = 'Data File (*.csv)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Select a data file',
            directory='*.csv',
            filter=file_filter,
            initialFilter='Excel File (*.csv)'
        )
        #filepath is the first object of the respone tuple
        filepath = response[0]
        print(response)

        #Open new *.csv file and write data to it
        with open(filepath, "w") as creating_new_csv_file:
            writer = csv.writer(creating_new_csv_file, lineterminator="\n")
            writer.writerow(self.analysisDataModel.headers)
            for row in range(self.analysisDataModel.model.rowCount()):
                print(row)
                #if self.analysisDataModel.model.record(row).value("name") != self.username:
                fields = []
                for col in range(self.analysisDataModel.model.columnCount()):
                    field = self.analysisDataModel.model.index(row, col).data()
                    fields.append(field)
                writer.writerow(fields)


    def updateFilter(self,s):
        filterStr = 'Name LIKE "%{}%"'.format(s)
        self.analysisDataModel.model.setFilter(filterStr)



    def plotData(self):

        row = self.table.currentIndex().row()
        # Problem Werte in float umwandeln
        carbon = self.analysisDataModel.model.record(row).value("carbon")
        print(type(carbon))
        hydrogen = self.analysisDataModel.model.record(row).value("hydrogen")
        print(type(hydrogen))
        nitrogen = self.analysisDataModel.model.record(row).value("nitrogen")
        print(type(nitrogen))
        sulfur = self.analysisDataModel.model.record(row).value("sulfur")
        print(type(sulfur))
        ash = self.analysisDataModel.model.record(row).value("ash")
        print(type(ash))
        moisture = self.analysisDataModel.model.record(row).value("analysis_moisture")
        print(type(moisture))

        oxygen = oxygen_calc(moisture, ash , carbon, hydrogen, nitrogen, sulfur)
        print(oxygen)
        data = [(carbon, hydrogen, nitrogen, sulfur, oxygen, ash, moisture)]
        print(data)
        Data = namedtuple('Data', ['name', 'value', 'primary_color'])
        carbonData = Data('Carbon',carbon, QColor("#000000"))
        hydrogenData = Data('Hydrogen', hydrogen, QColor("#008000"))
        nitrogenData = Data('Nitrogen', nitrogen, QColor("#82d3e5"))
        sulfurData = Data('Sulfur', sulfur, QColor("#FFFF00"))
        oxygenData = Data('Oxygen', oxygen, QColor("#0000FF"))
        ashData = Data('Ash', ash, QColor("#C0C0C0"))
        moistureData = Data('Moisture', ash, QColor("#00FFFF"))
        datas = [carbonData, hydrogenData, nitrogenData, sulfurData, oxygenData, ashData, moistureData]
        # self.passingInformation(data)
        self.passingInformation(datas)


    def passingInformation(self, datas):
        self.PlotWindow = PlotWindow()
        self.PlotWindow.datas = datas
        self.PlotWindow.create_piechart()
        self.PlotWindow.show()


class DataInputWindow(QDialog):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        #self.login = LoginGUI(self)


        # self.setFixedSize(300, 450)
        self.setWindowTitle("Process and Analysis Data Input")
        self.data = None
        self.setupUI()

    def setupUI(self):
        # Groupboxes
        """Setup the Add Contact dialog's GUI."""
        self.createTopLayout()
        self.createTopLeftGroupBox()
        self.createTopMiddleGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLayout()
        self.createBottomButtons()

        mainLayout = QGridLayout()

        mainLayout.addLayout(self.topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.topMiddleGroupBox, 2, 1)
        mainLayout.addWidget(self.topRightGroupBox, 2, 2)
        mainLayout.addLayout(self.bottomBoxes, 3, 0, 1, 3)

        mainLayout.addWidget(self.bottomButtonBox, 4, 2, 1, 1)

        self.setLayout(mainLayout)

    def createTopLayout(self):
        self.topLayout = QHBoxLayout()

        self.comboProzess = QComboBox()
        self.comboProzess.addItems(['--', 'RAW', 'HTC', ])
        self.comboLabel = QLabel("Process")
        self.combo = [self.comboLabel, self.comboProzess]

        self.sampleIn = QLineEdit()
        # self.sample_in.setFixedWidth()
        self.sampleInLabel = QLabel('Sample')
        self.sample = [self.sampleInLabel, self.sampleIn]

        items = [self.combo, self.sample]

        for elements in items:
            for j in elements:
                self.topLayout.addWidget(j)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Process Data")

        topLayout = QHBoxLayout()
        labelLeftV = QVBoxLayout()

        self.temperatureIn = QDoubleSpinBox()
        self.temperatureIn.setRange(0.00, 300.00)
        self.temperatureIn.setValue(0.00)
        self.temperatureInLabel = QLabel('Temperature')
        self.temperatureInUnit = QLabel('  °C')
        self.temperature = [self.temperatureIn, self.temperatureInUnit]

        self.pressureIn = QDoubleSpinBox()
        self.pressureIn.setRange(0.00, 100.00)
        self.pressureIn.setValue(0.00)
        self.pressureInLabel = QLabel('Pressure')
        self.pressureInUnit = QLabel('  bar')
        self.pressure = [self.pressureIn, self.pressureInUnit]

        self.dwellTimeIn = QDoubleSpinBox()
        self.dwellTimeIn.setRange(0.00, 1000.00)
        self.dwellTimeIn.setValue(0.00)
        self.dwellTimeInLabel = QLabel('Residence time')
        self.dwellTimeInUnit = QLabel('min')
        self.dwell_time = [self.dwellTimeIn, self.dwellTimeInUnit]

        labelLeftV.addWidget(self.temperatureInLabel)
        labelLeftV.addWidget(self.pressureInLabel)
        labelLeftV.addWidget(self.dwellTimeInLabel)


        self.processLayout = [self.temperature, self.pressure, self.dwell_time]
        processLayout = self.layoutBox(self.processLayout, Qt.AlignmentFlag.AlignLeft)

        topLayout.addLayout(labelLeftV)
        topLayout.addLayout(processLayout)

        self.topLeftGroupBox.setLayout(topLayout)

    def createTopMiddleGroupBox(self):
        self.topMiddleGroupBox = QGroupBox("Ultimate Analysis")

        topLayout = QHBoxLayout()
        labelLeftV = QVBoxLayout()

        self.carbonIn = QDoubleSpinBox()
        self.carbonInLabel = QLabel('Carbon')
        self.carbonInUnit = QLabel('wt%')
        self.carbon = [self.carbonIn, self.carbonInUnit]

        self.hydrogenIn = QDoubleSpinBox()
        self.hydrogenInLabel = QLabel('Hydrogen')
        self.hydrogenInUnit = QLabel('wt%')
        self.hydrogen = [self.hydrogenIn, self.hydrogenInUnit]

        self.nitrogenIn = QDoubleSpinBox()
        self.nitrogenInLabel = QLabel('Nitrogen')
        self.nitrogenInUnit = QLabel('wt%')
        self.nitrogen = [self.nitrogenIn, self.nitrogenInUnit]

        self.sulfurIn = QDoubleSpinBox()
        self.sulfurInLabel = QLabel('Sulfur')
        self.sulfurInUnit = QLabel('wt%')
        self.sulfur = [self.sulfurIn, self.sulfurInUnit]

        self.analysisLayout = [self.carbon, self.hydrogen, self.nitrogen, self.sulfur]
        analysisLayout = self.layoutBox(self.analysisLayout, Qt.AlignmentFlag.AlignRight)

        self.inputsAnalysis = [self.carbonIn, self.hydrogenIn, self.nitrogenIn, self.sulfurIn]
        self.defineDataInputAnalysis(self.inputsAnalysis)

        labelLeftV.addWidget(self.carbonInLabel)
        labelLeftV.addWidget(self.hydrogenInLabel)
        labelLeftV.addWidget(self.nitrogenInLabel)
        labelLeftV.addWidget(self.sulfurInLabel)

        topLayout.addLayout(labelLeftV)
        topLayout.addLayout(analysisLayout)

        self.topMiddleGroupBox.setLayout(topLayout)






    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Proximate Analysis")

        topLayout = QHBoxLayout()
        labelLeftV = QVBoxLayout()

        self.ashIn = QDoubleSpinBox()
        self.ashInLabel = QLabel('Ash')
        self.ashInUnit = QLabel('wt%')
        self.ash = [self.ashInLabel, self.ashIn, self.ashInUnit]

        self.moistureIn = QDoubleSpinBox()
        self.moistureInLabel = QLabel('Moisture')
        self.moistureInUnit = QLabel('wt%')
        self.moisture = [self.moistureInLabel, self.moistureIn, self.moistureInUnit]

        self.volatilesIn = QDoubleSpinBox()
        self.volatilesInLabel = QLabel('Volatiles')
        self.volatilesInUnit = QLabel('wt%')
        self.volatiles = [self.volatilesInLabel, self.volatilesIn, self.volatilesInUnit]

        self.analysisLayout = [self.ash, self.moisture, self.volatiles]
        analysisLayout = self.layoutBox(self.analysisLayout, Qt.AlignmentFlag.AlignRight)

        self.inputsProximate = [self.ashIn, self.moistureIn, self.volatilesIn]
        self.defineDataInputAnalysis(self.inputsProximate)

        self.inputsAnalysis = [self.carbonIn, self.hydrogenIn, self.nitrogenIn, self.sulfurIn]
        self.defineDataInputAnalysis(self.inputsAnalysis)

        labelLeftV.addWidget(self.ashInLabel)
        labelLeftV.addWidget(self.moistureInLabel)
        labelLeftV.addWidget(self.volatilesInLabel)

        topLayout.addLayout(labelLeftV)
        topLayout.addLayout(analysisLayout)

        self.topRightGroupBox.setLayout(topLayout)

    def createBottomLayout(self):
        self.createLeftBottomGroupBox()
        self.createRightBottomGroupBox()

        self.bottomBoxes = QHBoxLayout()
        self.bottomBoxes.addWidget(self.bottomLeftGroupBox)
        self.bottomBoxes.addWidget(self.bottomRightGroupBox)

    def createRightBottomGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Lower Heating Value")

        self.heatingValueIn = QDoubleSpinBox()
        self.heatingValueIn.setRange(0.00, 100000.00)
        self.heatingValueIn.setValue(0.00)
        self.heatingValueInLabel = QLabel('Lower Heating value')
        self.heatingValueInUnit = QLabel('J/g')
        heatingValue = [[self.heatingValueInLabel, self.heatingValueIn, self.heatingValueInUnit]]
        analysisLayout = self.layoutBox(heatingValue, Qt.AlignmentFlag.AlignCenter)
        self.bottomRightGroupBox.setLayout(analysisLayout)

    def createLeftBottomGroupBox(self):

        self.bottomLeftGroupBox = QGroupBox("Process Additives")
        layoutFbox = QFormLayout()
        #layoutFbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.additivesIn = QLineEdit()
        self.additivesIn.setFixedWidth(300)
        self.additivesInLabel = QLabel('Additives')
        additives = [[self.additivesInLabel, self.additivesIn]]
        analysisLayout = self.layoutBox(additives, Qt.AlignmentFlag.AlignCenter)
        self.bottomLeftGroupBox.setLayout(analysisLayout)

    def createBottomButtons(self):

        self.bottomButtonBox = QDialogButtonBox(self)
        self.bottomButtonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.bottomButtonBox.accepted.connect(self.accept)
        self.bottomButtonBox.rejected.connect(self.reject)

    def layoutBox(self, items, alignment):
        layout = QVBoxLayout()
        for elements in items:
            self.widget1 = QWidget()
            layout_h = QHBoxLayout(self.widget1)
            layout_h.setAlignment(alignment)
            for j in elements:
                layout_h.addWidget(j)
            layout.addWidget(self.widget1)
        return layout


    def defineDataInputAnalysis(self, items):
        for i in items:
            i.setRange(0.00, 100.00)
            i.setValue(0.00)

    def accept(self):
        self.data = []
        print(type(self.moistureIn.value()))
        for input in (
        self.username,self.sampleIn.text(),self.comboProzess.currentText(), self.carbonIn.value(), self.hydrogenIn.value(), self.nitrogenIn.value(),self.sulfurIn.value(), self.ashIn.value(), self.volatilesIn.value(),self.moistureIn.value(),
        self.temperatureIn.value(), self.pressureIn.value(), self.dwellTimeIn.value(), self.additivesIn.text(), self.heatingValueIn.value()):
            self.data.append(input)

        super().accept()




    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()
        else:
            pass

    def buttonStyle(self, buttons):

        for i in buttons:
            i.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: "white";
                border-radius: 5px;
                border-style: outset;
                border-width: 1px;
                border-color: lightgrey;
                color: "black"
            }
            QPushButton:hover {
                background-color: lightgray;
                border-color: grey;
            }
            """)

class PlotWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pie Chart of Components")
        self.setGeometry(100, 100, 750, 750)


    def create_piechart(self):
        offset = 180
        series = QPieSeries()
        series.setPieStartAngle(offset)
        series.setPieEndAngle(offset + 360)

        slices = list()
        for data in self.datas:
            slice = QPieSlice(data.name, data.value)
            slice.setLabelVisible(True)
            slice.setColor(data.primary_color)
            slice.setLabelBrush(data.primary_color)
            slice.setLabel(f"{data.name} {data.value} %")
            slices.append(slice)

        for slice in slices:
            series.append(slice)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        chart.setTitle("Pie Chart of Components")



        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setCentralWidget(chartview)




