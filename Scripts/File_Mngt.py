from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os

class FileMngt():
    curr_dir = os.path.abspath(os.getcwd())
    def OpenDirectoryDialog(self):
        self.curr_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', self.curr_dir, QFileDialog.ShowDirsOnly)
        return self.curr_dir
    
    def OpenFileWithExtensionDialog(self, p_filter):
        self.curr_path, _ = QFileDialog.getOpenFileName(None, 'Select a file:', self.curr_dir, p_filter)
        return self.curr_path
    
    def SaveFile(self, p_path, p_pixmap):
        p_pixmap.save(p_path, "png")
    
    def LoadFolder(self):
        path = self.OpenDirectoryDialog()
        if path != "":
            images_data = []
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images_data.append(file_path)
            return images_data
        else:
            return []

    def SaveData(self, p_data):
        location = self.OpenDirectoryDialog()
        name = p_data[2]
        pixmap = p_data[4]
        path = os.path.join(location, name)
        self.SaveFile(path, pixmap)

    def GetFileName(self, p_path):
        return os.path.basename(p_path)
    
    def CreateFolder(self, p_directory, p_name):
        directory = os.path.join(p_directory, str(p_name))
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory
    
    def CreateFilePath(self, p_location, p_name):
        return os.path.join(p_location, p_name)