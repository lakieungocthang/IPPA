from Scripts.Base_AI import *
from Resources.Gui.ui_reconstructor import Ui_Reconstructor

DEPTH_PATH = ""
MODEL_STATUS = True

class Reconstructor(Base):
    updateReconstructorResult = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.depth_path = ""
        self.actual_size = QSize()
        self.depth_gray = QPixmap()

    def UpdateDisplayMask(self, p_pixmap):
        mask = p_pixmap.scaledToWidth(350, Qt.SmoothTransformation)
        self.ui.reconstructorMask.setPixmap(mask)

# -------------------------------------------------------------------------------------------------

    def Initialize(self):
        self.ui = Ui_Reconstructor()
        self.ui.setupUi(self)
        self.SetupBrowser(self.ui.reconstructorLayout, DEPTH_PATH)
        self.ResetData()

    def OnBrowseClicked(self):
        self.depth_path = self.fileMngt.OpenFileWithExtensionDialog("*.png *.jpg")
        if self.depth_path == "":
            print("Choose mask fail!")
        else:
            self.modelBrowser.SetModelPath(self.depth_path)
            self.depth_gray = cv2.imread(self.depth_path, 0)
        
    def Inference(self, p_image):
        print("reconstructing")
        if not p_image.isNull() and self.depth_path != "":
            self.model_status = False
            cv_img = qpixmap_to_cv2(p_image)

            self.updateReconstructorResult.emit([cv_img, self.depth_gray])
            return [True, [], None]
        else:
            return [None, None, None]

    def Predict(self, p_mode):
        if p_mode == "list":
            # location = self.fileMngt.CreateFolder("result")
            # progress_dialog = CreateProgressDialog("Progress", "Processing images...", len(self.image_path_list))
            # for i, path in enumerate(self.image_path_list):
            #     if progress_dialog.wasCanceled():
            #         break  # Exit the loop if the user cancels
            #     progress_dialog.setValue(i)
            print("list")
        else:
            ret, data, out_image = self.Inference(self.input_image)
            if out_image != None:
                self.SetOutputImage(out_image)
            if ret == None: return
            elif ret == True and p_mode == "single":
                pass
