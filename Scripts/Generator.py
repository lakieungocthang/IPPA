from Scripts.Base_AI import *
from Resources.Gui.ui_generator import Ui_Generator
from Ai.Generatator.Network import *

MODEL_FICE_PATH = "Ai/Generatator/cyclegan_wli2fice.pth"
MODEL_LCI_PATH = "Ai/Generatator/cyclegan_wli2lci.pth"

class Generator(Base):
    updateGeneratorFiceResult = pyqtSignal(list)
    updateGeneratorLciResult = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.generator_mode = "FICE"

    def OnLightModeChanged(self, p_text):
        if p_text == "FICE":
            self.generator_mode = "FICE"
            self.model_path = MODEL_FICE_PATH
            self.modelBrowser.SetModelPath(self.model_path)
            self.SetupModel()
        if p_text == "LCI":
            self.generator_mode = "LCI"
            self.model_path = MODEL_LCI_PATH
            self.modelBrowser.SetModelPath(self.model_path)
            self.SetupModel()

# -------------------------------------------------------------------------------------------------

    def Initialize(self):
        self.ui = Ui_Generator()
        self.ui.setupUi(self)
        self.model_path = MODEL_FICE_PATH
        self.ui.cbb_lightMode.currentTextChanged.connect(self.OnLightModeChanged)
        self.SetupBrowser(self.ui.generateLayout, self.model_path)
        self.ResetData()
        
    def SetupModel(self):
        if self.model_path == "":
            print("Not valid model path")
        else:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = define_G(3, 3, 64, 'resnet_9blocks', use_dropout=False, init_type='normal', init_gain=0.02, norm='instance')
            state_dict = torch.load(self.model_path, map_location=str(device))
            self.model.load_state_dict(state_dict)
            print("Model is loaded")

    def Inference(self, p_image):
        print("generating")
        if not p_image.isNull():
            self.model_status = False
            tensor = qpixmap_to_tensor(p_image, transform_generate, device)
            with torch.no_grad():
                self.model.to(device)
                output = self.model(tensor.to(device))
                
                output = output.detach().cpu()
                output_pil = de_transfrom_generate(output.squeeze(0))

                output_pix = pil_to_qpixmap(output_pil)
                if self.generator_mode == "FICE":
                    self.updateGeneratorFiceResult.emit([output_pix])
                if self.generator_mode == "LCI":
                    self.updateGeneratorLciResult.emit([output_pix])
                return [True, [], output_pix]
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
