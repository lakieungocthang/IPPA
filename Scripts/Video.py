import cv2, time
from collections import deque

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from Resources.Gui.ui_video import Ui_Video
from Scripts.File_Mngt import FileMngt

class VideoThread(QThread):
    update_duration = pyqtSignal(int, int)  # Emit current frame and total frames

    def __init__(self, buffer):
        super().__init__()
        self.live_flag = False
        self.run_flag = False
        self.video_path = 0
        self.buffer = buffer

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = 1.0 / fps if fps > 0 else 0.0166  # Default to 30 FPS if unable to get FPS
        current_frame = 0

        while self.live_flag:
            if self.run_flag:
                start_time = time.time()
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    if len(self.buffer) < 5:  # Limit buffer size to 5 frames
                        self.buffer.append(frame)
                    current_frame += 1
                    self.update_duration.emit(current_frame, total_frames)
                else:
                    break
                elapsed_time = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed_time)
                time.sleep(sleep_time)
        cap.release()

    def ChangeState(self, p_state):
        if p_state == "play":
            self.live_flag = True
            self.run_flag = True
        if p_state == "pause":
            self.run_flag = False
        if p_state == "stop":
            self.live_flag = False
            self.run_flag = False
            self.wait()

    def SetVideoPath(self, p_path):
        self.video_path = p_path

class Video(QWidget):
    startSignal = pyqtSignal()
    stopSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Video()
        self.ui.setupUi(self)
        self.fileMngt = FileMngt()

        self.is_playing = False
        self.video_path = ""
        self.ui.videoPath.setText(self.video_path)
        self.frame_buffer = deque(maxlen=10)
        self.thread = VideoThread(self.frame_buffer)

        self.ui.progressBar.setRange(0, 100)
        self.ui.timer.setText("00:00 / 00:00")

        self.ui.btn_play_pause.clicked.connect(self.TogglePlayPause)
        self.ui.btn_stop.clicked.connect(self.StopVideo)
        self.ui.btn_browse.clicked.connect(self.OnBrowseClicked)

        # Connect the update_frame signal to update the progress bar and timer
        self.thread.update_duration.connect(self.UpdateProgress)

    def TogglePlayPause(self):
        if self.is_playing:
            self.PauseVideo()
        else:
            self.StartVideo()

    def StartVideo(self):
        if self.thread.live_flag == False:
            if self.video_path == "":
                return
            self.thread.SetVideoPath(self.video_path)
            self.thread.ChangeState("play")
            self.thread.start()
            self.startSignal.emit()
        else:
            self.thread.ChangeState("play")
        print("start")
        self.is_playing = True
        self.ui.btn_play_pause.setIcon(QIcon(":/Icons/Resources/Icons/pause.svg"))

    def PauseVideo(self):
        self.thread.ChangeState("pause")
        self.is_playing = False
        self.ui.btn_play_pause.setIcon(QIcon(":/Icons/Resources/Icons/play.svg"))
        print("pause")

    def StopVideo(self):
        self.thread.ChangeState("stop")
        self.stopSignal.emit()
        self.is_playing = False
        self.frame_buffer.clear()
        self.ui.btn_play_pause.setIcon(QIcon(":/Icons/Resources/Icons/play.svg"))
        self.ui.progressBar.setValue(0)  # Reset progress bar
        self.ui.timer.setText("00:00 / 00:00")  # Reset timer
        print("stop")

    def OnBrowseClicked(self):
        self.video_path = self.fileMngt.OpenFileWithExtensionDialog("*.mp4 *.avi")
        if self.video_path == "":
            print("Choose video fail! Please choose again!")
        else:
            self.ui.videoPath.setText(self.video_path)
            self.frame_buffer.clear()

    def UpdateProgress(self, current_frame, total_frames):
        if total_frames > 0:
            progress = int((current_frame / total_frames) * 100)
            self.ui.progressBar.setValue(progress)

            current_time = self.FrameToTime(current_frame)
            total_time = self.FrameToTime(total_frames)
            self.ui.timer.setText(f"{current_time} / {total_time}")

    def FrameToTime(self, frame_number, fps=30):
        """ Convert frame number to time in MM:SS format. """
        total_seconds = int(frame_number / fps)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def GetFrame(self):
        if self.frame_buffer:
            return self.frame_buffer.popleft()
        return None
