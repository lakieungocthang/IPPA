from ultralytics import YOLO

from Scripts.Base_AI import *
from Resources.Gui.ui_tracker import Ui_Tracker
from Ai.Track.StrongSort import StrongSORT

MODEL_PATH = "Ai/Track/5-class-model.pt"
TRACKER_PATH = "Ai/Track/osnet_x0_25_endocv_30.pt"
MODEL_STATUS = True

class Tracker(Base):
    updateTrackerResult = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        
    def SetupResource(self):
        self.trackerModule = StrongSORT(TRACKER_PATH, torch.device(device=0), fp16 = False, max_dist=0.95, max_iou_dist=0.95, max_age=300)
# ===================================================Body=======================================================

    def Initialize(self):
        self.ui = Ui_Tracker()
        self.ui.setupUi(self)
        self.model_path = MODEL_PATH
        self.SetupBrowser(self.ui.trackLayout, MODEL_PATH)
        self.SetupVideo(self.ui.trackLayout)
        self.SetupResource()
        self.ResetData()

    def SetupModel(self):
        if self.model_path == "":
            print("Not valid model path")
        else:
            self.model = YOLO(self.model_path)
            print("Model is loaded")

    # def UpdateInputImage(self, p_image):
    #     self.input_image = p_image
    #     if self.model_status:
    #         self.Inference(p_silent=True)

    def Inference(self, p_image):
        print("tracking")
        if not p_image.isNull():
            # self.model_status = False
            cv_img = qpixmap_to_cv2(p_image)
            yolo_input = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
            result = self.model(yolo_input)[0]
            # result_image = p_image
            previous_tracks = []
            # any_trackers = False
            if result and len(result.boxes) > 0:
                # any_trackers = True
                tracks = self.trackerModule.update(result.boxes.data.to("cpu").numpy(), yolo_input)
                if len(tracks.shape) == 2 and tracks.shape[1] == 8:
                    if len(previous_tracks) > 0:
                        tracks = self.UpdateTrackId(tracks, previous_tracks)
                    result_tracking = self.DrawTrack(yolo_input, tracks)
                    previous_tracks = tracks
                    result_image = cv2_to_qpixmap(cv2.cvtColor(result_tracking, cv2.COLOR_BGR2RGB))
                    return [True, [], result_image]
                else:
                    return [False, [], p_image]
            else:
                return [None, None, p_image]
        else:
            return [None, None, None]

    def Predict(self, p_mode):
        ret, data, out_image = self.Inference(self.input_image)
        if out_image != None:
            self.SetOutputImage(out_image)
        if ret == None: return
        elif ret == True and p_mode == "single":
            pass
        elif ret == True and p_mode == "video":
            pass

    def UpdateTrackId(self, current_tracks, previous_tracks):
        updated_tracks = []
        for current_track in current_tracks:
            min_distance = float('inf')
            matching_track_id = None
            for previous_track in previous_tracks:
                if current_track[6] != previous_track[6]:
                    continue
                iou = self.calculate_iou(current_track[:4], previous_track[:4])
                if iou > self.iou_threshold:
                    if self.use_frame_id:
                        time_diff = abs(current_track[3] - previous_track[3])
                        if time_diff < min_distance:
                            min_distance = time_diff
                            matching_track_id = previous_track[4]
                    else:
                        time_diff = abs(current_track[1] - previous_track[1])
                        if time_diff < min_distance:
                            min_distance = time_diff
                            matching_track_id = previous_track[4]

            if matching_track_id is not None:
                current_track[4] = matching_track_id
            updated_tracks.append(current_track)
        return updated_tracks

    def DrawTrack(self, frame, tracks):
        for track in tracks:
            x1, y1, x2, y2 = int(track[0]), int(track[1]), int(track[2]), int(track[3])
            cv2.rectangle(frame, (x1,y1), (x2, y2), (255, 0, 0), 5)
        return frame
