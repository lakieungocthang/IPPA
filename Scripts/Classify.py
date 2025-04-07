from Scripts.Base_AI import *
from Resources.Gui.ui_classify import Ui_Classify

MODEL_PATH = "./Ai/Classify/MBNet_Adam_Focal_6.pt"
MODEL_STATUS = True

class Classify(Base):
    updateClassifyResult = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        
    def SetupResource(self):
        self.lstParts = ["Hau hong","Thuc quan","Tam vi","Than vi","Phinh vi","Hang vi","Bo cong lon","Bo cong nho","Hanh ta trang","Ta trang","Non"]
        # lstPartsImage = ["HauHong.png","ThucQuan.png","TamVi.png","ThanVi.png","PhinhVi.png","HangVi.png","BoCongLon.png","BoCongNho.png","HanhTaTrang.png","TaTrang.png","Non-color.png"]
        img1 = QPixmap("./Resources/Parts/HauHong.png")
        img2 = QPixmap("./Resources/Parts/ThucQuan.png")
        img3 = QPixmap("./Resources/Parts/TamVi.png")
        img4 = QPixmap("./Resources/Parts/ThanVi.png")
        img5 = QPixmap("./Resources/Parts/PhinhVi.png")
        img6 = QPixmap("./Resources/Parts/HangVi.png")
        img7 = QPixmap("./Resources/Parts/BoCongLon.png")
        img8 = QPixmap("./Resources/Parts/BoCongNho.png")
        img9 = QPixmap("./Resources/Parts/HanhTaTrang.png")
        img10 = QPixmap("./Resources/Parts/TaTrang.png")
        img11 = QPixmap("./Resources/Parts/Non-color.png")
        self.lstPartsImage = [img1,img2,img3,img4,img5,img6,img7,img8,img9,img10,img11]

# ===================================================Body=======================================================

    def Initialize(self):
        self.ui = Ui_Classify()
        self.ui.setupUi(self)
        self.model_path = MODEL_PATH
        self.SetupBrowser(self.ui.classifyLayout, MODEL_PATH)
        self.SetupVideo(self.ui.classifyLayout)
        self.SetupResource()
        self.ResetData()

        self.ui.btn_executeAll.clicked.connect(self.OnExecuteAllClicked)

    def SetupModel(self):
        if self.model_path == "":
            print("Not valid model path")
        else:
            self.model = torch.jit.load(self.model_path, map_location=device)
            print("Model is loaded")

    def Inference(self, p_image):
        if not p_image.isNull():
            tensor = qpixmap_to_tensor(p_image, transform_classify, device)
            with torch.no_grad():
                output1, output2 = self.model(tensor.to(device))
                output1 = torch.argmax(torch.softmax(output1, dim=1), dim=1).item()

                output2 = torch.softmax(output2, dim=1)
                output2 = torch.argmax(output2, dim=1).item() - 4
                if output1 == 1:
                    predict_label = self.lstParts[output2]
                    self.ui.classifyResult.setText(predict_label)
                    pix = self.lstPartsImage[output2].scaled((self.ui.classifyDisplay.size() - QSize(2, 2)), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    return [True, [predict_label, pix], p_image]
                else:
                    return [False, None, p_image]
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
                self.ui.classifyDisplay.setPixmap(data[1])
                self.updateClassifyResult.emit(data)
            elif ret == True and p_mode == "video":
                self.ui.classifyDisplay.setPixmap(data[1])
            elif ret == False and p_mode == "single":
                Inform("Inform", "This image is unclear, choose another image")
