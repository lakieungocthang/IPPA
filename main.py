import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

from Scripts.App import MainWindow
os.environ.update({"QT_QPA_PLATFORM_PLUGIN_PATH":"/usr/local/lib/python3.10/site-packages/PyQt5/Qt5/plugins"})

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Arial", 16)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
