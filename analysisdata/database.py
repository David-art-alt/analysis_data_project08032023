# -*- coding :utf-8 -*-
# analysisdata/database.py

'''This module provides a database connection'''

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtSql import QSqlDatabase, QSqlQuery


def _createHtcDataTable():
# Create a query and execute it right away using .exec()
    createTableQuery = QSqlQuery()
    createTableQuery.exec(
        """
        CREATE TABLE IF NOT EXISTS analysisdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            name VARCHAR(40) NOT NULL,
            process VARCHAR(50),
            sample VARCHAR(40) NOT NULL,
            carbon REAL NOT NULL,
            hydrogen REAL NOT NULL,
            nitrogen REAL NOT NULL, 
            sulfur REAL NOT NULL,
            ash REAL NOT NULL, 
            volatiles REAL NOT NULL, 
            analysis_moisture REAL NOT NULL, 
            temperature REAL NOT NULL, 
            pressure REAL NOT NULL, 
            residence time REAL NOT NULL, 
            additives VARCHAR(40),
            lo heating REAL NOT NULL
        )
        """
    )



def createConnection(databaseName):
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName(databaseName)
    if not con.open():
        QMessageBox.critical(
            None,
            "VARESI Analysisdata!",
            f"Database Error: {con.lastError().text()}",
        )
        return False
    _createHtcDataTable()
    return True