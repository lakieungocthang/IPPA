from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from Scripts.Utils import *
from Scripts.Message import *
from Scripts.File_Mngt import FileMngt
from Scripts.Video import Video
from Resources.Gui.ui_modelBrowser import Ui_ModelBrowser


MODEL_STATUS = True

class ModelBrowser(QWidget):
    browseSignal = pyqtSignal()
    executeSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_ModelBrowser()
        self.ui.setupUi(self)
        self.default_model_path = ""

        self.ui.btn_browse.clicked.connect(self.OnBrowseClicked)
        self.ui.btn_execute.clicked.connect(self.OnExecuteClicked)

    def OnBrowseClicked(self):
        self.browseSignal.emit()

    def OnExecuteClicked(self):
        self.executeSignal.emit()
    
    def SetModelPath(self, p_path):
        self.ui.modelPath.setText(p_path)
    
    def SetDefaultPath(self, p_default_path):
        self.default_model_path = p_default_path

    def DisplayDefaultPath(self):
        self.ui.modelPath.setText(self.default_model_path)

class Base(QWidget):
    requestUpdateImage = pyqtSignal()
    requestImagesList = pyqtSignal()
    updateOutputImageSignal = pyqtSignal(object)
    def __init__(self):
        super().__init__()

        self.input_image = QPixmap()
        self.output_image = QPixmap()
        self.image_path_list = []
        self.model_path = ""
        self.model = None
        self.model_status = True
        self.new_image_flag = False # will be setted when self.input_image changed
        self.new_images_list_flag = False

        self.Initialize()

# ------------------------------------------------Setup model browser---------------------------------------------

    def SetupBrowser(self, p_layout, p_default_model_name):
        self.modelBrowser = ModelBrowser()
        p_layout.insertWidget(0, self.modelBrowser)
        self.fileMngt = FileMngt()
        self.modelBrowser.SetDefaultPath(p_default_model_name)
        self.modelBrowser.browseSignal.connect(self.OnBrowseClicked)
        self.modelBrowser.executeSignal.connect(self.OnExecuteClicked)

    def OnBrowseClicked(self):
        self.model_path = self.fileMngt.OpenFileWithExtensionDialog("*.pt *.pth")
        if self.model_path == "":
            print("Choose model fail!")
        else:
            self.UpdateModelPath(self.model_path)
            self.SetupModel()

    def OnExecuteClicked(self):
        self.requestUpdateImage.emit()
        self.WaitRequestUpdateImageResponse()

    def WaitRequestUpdateImageResponse(self):
        if self.new_image_flag:
            self.Predict(p_mode="single")
            self.new_image_flag = False
        else:
            QMetaObject.invokeMethod(self, "WaitRequestUpdateImageResponse", Qt.QueuedConnection)

# ------------------------------------------------Setup Video--------------------------------------------------

    def UpdateModelPath(self, p_path):
        self.modelBrowser.SetModelPath(p_path)

    def SetupVideo(self, p_layout):
        self.video = Video()
        p_layout.insertWidget(0, self.video)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.PredictFrameFromVideo)

        self.video.startSignal.connect(self.StartCollect)
        self.video.stopSignal.connect(self.StopCollect)

    def StartCollect(self):
        self.timer.start(10)

    def StopCollect(self):
        self.timer.stop()

    def PredictFrameFromVideo(self):
        frame = self.video.GetFrame()
        if frame is not None:
            image = cv2_to_qpixmap(frame)
            self.input_image = image
            self.Predict(p_mode="video")

# ===================================================Body=============================================================

    def SetInputImage(self, p_image):
        self.input_image = p_image
        self.new_image_flag = True

    def SetOutputImage(self, p_image):
        self.updateOutputImageSignal.emit(p_image)

    def SetImagesList(self, p_image_path_list):
        self.image_path_list = p_image_path_list
        self.new_images_list_flag = True

    def ResetData(self):
        self.model_status = MODEL_STATUS
        self.modelBrowser.DisplayDefaultPath()
        self.SetupModel()

    def OnExecuteAllClicked(self):
        self.requestImagesList.emit()
        self.WaitRequestImagesListResponse()
        
    def WaitRequestImagesListResponse(self):
        if self.new_images_list_flag:
            self.Predict(p_mode="list")
            self.new_images_list_flag = False
        else:
            QMetaObject.invokeMethod(self, "WaitRequestImagesListResponse", Qt.QueuedConnection)

    def SetupModel(self):
        pass

    def Initialize(self):
        pass

    def Predict(self, p_mode):
        pass

    def Inference(self, p_image):
        pass
