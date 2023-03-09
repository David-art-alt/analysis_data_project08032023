# -*- coding :utf-8 -*-
# analysisdata/model.py
'''This module provides a model to manage the analysis- and process data table.'''

from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtSql import QSqlTableModel
import csv

from PyQt6.QtWidgets import QHeaderView, QFileDialog, QTableView




class AnalysisDataModel():

    def __init__(self):

        self.model = self._createModel()


    #@staticmethod
    def _createModel(self):
        """Create and set uo the model."""
        tableModel = QSqlTableModel()
        tableModel.setTable("analysisdata")
        tableModel.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        tableModel.select()

        self.headers = ("ID","Name", "SampleID", "Process", "Carbon [wt%]", "Hydrogen [wt%]", "Nitrogen [wt%]", "Sulfur [wt%]","Ash [wt%]",
             "Volatiles [wt%]", "Analysis moisture [wt%]", "Temperature [°C]", "Pressure [bar]", "Residence time [min]", "Additives", "lo Heating value [J/g]")

        for columIndex, header in enumerate(self.headers):
            tableModel.setHeaderData(columIndex, Qt.Orientation.Horizontal, header)
            #print(header)

        return tableModel



    def addData(self, data):
        """Add data to the database."""
        rows = self.model.rowCount()
        self.model.insertRows(rows, 1)
        print('Rows',self.model.rowCount())
        for column, input in enumerate(data):
            print(rows, column, input)
            print(type(input))
            self.model.setData(self.model.index(rows, column+1), input)
        self.model.submitAll()
        self.model.select()

    def deleteData(self, row):
        """Remove data from the database"""
        self.model.removeRow(row)
        self.model.submitAll()
        self.model.select()
    '''
    def clearAll(self):
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.model.removeRows(0, self.model.rowCount())
        self.model.submitAll()
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
    '''



