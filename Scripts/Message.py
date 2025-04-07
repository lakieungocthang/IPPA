from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

def Inform(title, text):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()

def CreateProgressDialog(p_title, p_message, p_max_value):
    progress_dialog = QProgressDialog(p_message, "Cancel", 0, p_max_value)
    progress_dialog.setWindowTitle(p_title)
    progress_dialog.setWindowModality(Qt.WindowModal)  # Modal window that blocks interaction with the rest of the app
    progress_dialog.setMinimumDuration(0)
    return progress_dialog