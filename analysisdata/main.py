# -*- coding :utf-8 -*-
# analysisdata/main.py
'''This module provides VARESI application.'''

import sys

from PyQt6.QtWidgets import QApplication

from .views import MainWindow



def main():
    """Project main function"""
    # Create the application
    app = QApplication(sys.argv)
    window = MainWindow()
    # Run the event loop
    sys.exit(app.exec())