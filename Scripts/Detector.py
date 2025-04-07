from ultralytics import YOLO
from ultralytics.utils import ops

from Scripts.Base_AI import *
from Resources.Gui.ui_detector import Ui_Detector
from Scripts.Message import *

MODEL_PATH = "Ai/Detection/best_viemTQ.pt"
MODEL_ALL_PATH = "Ai/Detection/best_all.pt"
MODEL_STATUS = True

class Detector(Base):
    updateDetectionResult = pyqtSignal(list)
    def __init__(self):
        super().__init__()

# -------------------------------------------------------------------------------------------------

    def Initialize(self):
        self.ui = Ui_Detector()
        self.ui.setupUi(self)
        self.model_path = MODEL_ALL_PATH
        self.SetupBrowser(self.ui.detectorLayout, MODEL_PATH)
        self.ResetData()

        self.ui.cb_displaySegmentation.setChecked(False)
        self.ui.cb_displaySegmentation.stateChanged.connect(self.OnDisplaySegmentationChanged)
        self.ui.btn_executeAll.clicked.connect(self.OnExecuteAllClicked)

    def OnDisplaySegmentationChanged(self):
        if self.ui.cb_displaySegmentation.isChecked():
            self.model_path = MODEL_PATH
            self.SetupModel()
        else:
            self.model_path = MODEL_ALL_PATH
            self.SetupModel()
            
    def SetupModel(self):
        if self.model_path == "":
            print("Not valid model path")
        else:
            self.UpdateModelPath(self.model_path)
            self.model = YOLO(self.model_path)
            print("Model is loaded")

    def Inference(self, p_image):
        print("detecting")
        if not p_image.isNull():
            cv_img = qpixmap_to_cv2(p_image)
            yolo_input = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
            image_height, image_width = yolo_input.shape[:2]
            
            result = self.model(yolo_input)[0]
            
            if len(result.boxes) > 0:
                boxes = result.boxes.xyxy 
                scores = result.boxes.conf 
                classes = result.boxes.cls
                
                preds = torch.cat((boxes, scores.view(-1, 1), classes.view(-1, 1)), dim=1)
                preds = preds.unsqueeze(0)

                conf = 0.25
                iou = 0.45
                agnostic_nms = False
                max_det = 300
                classes = None
                
                preds = ops.non_max_suppression(preds, conf, iou, agnostic=agnostic_nms, max_det=max_det, classes=classes, nc=len(self.model.names))

                num_lesion = len(preds[0])
                
                if num_lesion > 0:
                    result_boxes = preds[0][:, :4].tolist()  # Get bounding box coordinates
                    classes_indices = preds[0][:, 5].int().tolist()  # Class indices
                    class_name = [self.model.names[int(cls)] for cls in classes_indices][0]

                    x1, y1, x2, y2 = map(int, result_boxes[0])
                    
                    # Draw rectangle and label
                    cv2.rectangle(yolo_input, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    text = f'{class_name}: {conf:.2f}'
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1  
                    thickness = 2  
                    text_color = (255, 255, 255) 
                    outline_color = (0, 0, 0)  
                    (text_width, text_height), _ = cv2.getTextSize(text, font, fontScale, thickness)
                    text_x, text_y = x1, y1 - 10
                    cv2.putText(yolo_input, text, (text_x - 1, text_y - 1), font, fontScale, outline_color, thickness + 2)
                    cv2.putText(yolo_input, text, (text_x + 1, text_y - 1), font, fontScale, outline_color, thickness + 2)
                    cv2.putText(yolo_input, text, (text_x - 1, text_y + 1), font, fontScale, outline_color, thickness + 2)
                    cv2.putText(yolo_input, text, (text_x + 1, text_y + 1), font, fontScale, outline_color, thickness + 2)
                    cv2.putText(yolo_input, text, (text_x, text_y), font, fontScale, text_color, thickness)
                    
                    # Draw segmentation when check box is checked
                    if self.ui.cb_displaySegmentation.isChecked():
                        mask = result.masks.data[0].cpu().numpy()
                        mask_resized = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_NEAREST)
                        mask_binary = (mask_resized > 0.5).astype(np.uint8)  # Threshold mask
                        # Find contours from the mask
                        contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        cv2.drawContours(yolo_input, contours, -1, (0, 255, 0), 2)  # Green contours, thickness=2
                    result_image = cv2_to_qpixmap(cv2.cvtColor(yolo_input, cv2.COLOR_BGR2RGB))
                    
                    return [True, [num_lesion, result_image, [class_name, result_boxes]], result_image]
            else:
                return [False, None, p_image]

        else:
            return [None, None, None]

    def Predict(self, p_mode):
        if p_mode == "list":
            direction = self.fileMngt.OpenDirectoryDialog()
            location = self.fileMngt.CreateFolder(direction, "result")
            progress_dialog = CreateProgressDialog("Progress", "Processing images...", len(self.image_path_list))
            for i, path in enumerate(self.image_path_list):
                if progress_dialog.wasCanceled():
                    break  # Exit the loop if the user cancels
                progress_dialog.setValue(i)

                image = QPixmap(path)
                ret, data, out_image = self.Inference(image)
                if out_image != None:
                    name = self.fileMngt.GetFileName(path)
                    path = self.fileMngt.CreateFilePath(location, name)
                    out_image.save(path)
        else:
            ret, data, out_image = self.Inference(self.input_image)
            if out_image != None:
                self.SetOutputImage(out_image)
            if ret == None: return
            elif ret == True and p_mode == "single":
                self.ui.detectorResult.setText(str(data[0]))
                self.updateDetectionResult.emit(data)
            elif ret == False and p_mode == "single":
                Inform("Inform", "There are no detection")
                
