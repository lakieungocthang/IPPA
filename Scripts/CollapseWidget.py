import random

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from Resources.Gui.ui_edit import Ui_Edit
from Resources.Gui.ui_report import Ui_Report
from Resources.Gui.ui_report_sort import Ui_ReportSort
from Resources.Gui.ui_report_main import UiReportMain
from Resources.Gui.ui_transform import Ui_Transform
from Scripts.File_Mngt import FileMngt


class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.on_pressed)

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))

    def on_pressed(self):
        checked = not self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.toggle_animation.setDirection(QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward)
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (self.sizeHint().height() - self.content_area.maximumHeight())
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(100)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(100)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class CropWidget(QWidget):
    def __init__(self):
        super().__init__()

        vboxlayout = QVBoxLayout(self)
        vboxlayout.setAlignment(Qt.AlignTop)
        collapsibleBox = CollapsibleBox("Crop")
        collapsibleBox.toggle_button.setChecked(True)
        vboxlayout.addWidget(collapsibleBox)

        lay = QVBoxLayout()
        for j in range(5):
            label = QLabel("{}".format(j))
            color = QColor(*[random.randint(0, 255) for _ in range(3)])
            label.setStyleSheet(
                "background-color: {}; color : white;".format(color.name())
            )
            label.setAlignment(Qt.AlignCenter)
            lay.addWidget(label)

        collapsibleBox.setContentLayout(lay)


class TransformWidget(QWidget):
    cropSignal = pyqtSignal()
    noCropSignal = pyqtSignal()
    keepRatioSignal = pyqtSignal()
    ignoreRatioSignal = pyqtSignal()
    allFilesSignal = pyqtSignal()
    oneFileSignal = pyqtSignal()
    executeSignal = pyqtSignal()
    widthChangedSignal = pyqtSignal()
    heightChangedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Transform()
        self.ui.setupUi(self)

        self.fileMngt = FileMngt()

        self.ui.browseButton.clicked.connect(self.OnBrowseClicked)
        self.ui.cropButton.clicked.connect(self.signalToCrop)
        self.ui.allFilesButton.clicked.connect(self.signalToAllFiles)
        self.ui.executeButton.clicked.connect(self.signalToExecute)
        self.ui.ratioButton.toggled.connect(self.signalToRatio)
        self.ui.widthBox.valueChanged.connect(self.signalToWidth)
        self.ui.heightBox.valueChanged.connect(self.signalToHeight)
        self.ui.resolutionBox.currentIndexChanged.connect(self.SetStandardResolution)

    def ratioButtonCheckable(self):
        self.ui.ratioButton.setCheckable(True)

    def ratioButtonUncheckable(self):
        self.ui.ratioButton.setChecked(False)
        self.ui.ratioButton.setCheckable(False)

    def SetStandardResolution(self):
        if self.ui.resolutionBox.currentText() == 'SD':
            self.ui.widthBox.setValue(720)
            self.ui.heightBox.setValue(480)
            self.ratioButtonUncheckable()
        elif self.ui.resolutionBox.currentText() == 'XGA':
            self.ui.widthBox.setValue(1024)
            self.ui.heightBox.setValue(768)
            self.ratioButtonUncheckable()
        elif self.ui.resolutionBox.currentText() == 'HD':
            self.ui.widthBox.setValue(1280)
            self.ui.heightBox.setValue(720)
            self.ratioButtonUncheckable()
        elif self.ui.resolutionBox.currentText() == 'SXGA':
            self.ui.widthBox.setValue(1280)
            self.ui.heightBox.setValue(1024)
            self.ratioButtonUncheckable()
        elif self.ui.resolutionBox.currentText() == 'Full HD':
            self.ui.widthBox.setValue(1920)
            self.ui.heightBox.setValue(1080)
            self.ratioButtonUncheckable()
        else:
            self.ratioButtonCheckable()

    def SetCurrentStandard(self):
        if self.ui.widthBox.value() == 720 and self.ui.heightBox.value() == 480:
            self.ui.resolutionBox.setCurrentIndex(1)
        elif self.ui.widthBox.value() == 1024 and self.ui.heightBox.value() == 768:
            self.ui.resolutionBox.setCurrentIndex(2)
        elif self.ui.widthBox.value() == 1280 and self.ui.heightBox.value() == 720:
            self.ui.resolutionBox.setCurrentIndex(3)
        elif self.ui.widthBox.value() == 1280 and self.ui.heightBox.value() == 1024:
            self.ui.resolutionBox.setCurrentIndex(4)
        elif self.ui.widthBox.value() == 1920 and self.ui.heightBox.value() == 1080:
            self.ui.resolutionBox.setCurrentIndex(5)
        else:
            self.ui.resolutionBox.setCurrentIndex(0)
            self.ratioButtonCheckable()

    def signalToWidth(self):
        self.SetCurrentStandard()
        self.widthChangedSignal.emit()

    def signalToHeight(self):
        self.SetCurrentStandard()
        self.heightChangedSignal.emit()

    def signalToCrop(self):
        if self.ui.cropButton.isChecked():
            self.cropSignal.emit()
        else:
            self.noCropSignal.emit()

    def signalToRatio(self):
        if self.ui.ratioButton.isChecked():
            self.keepRatioSignal.emit()
        else:
            self.ignoreRatioSignal.emit()

    def OnBrowseClicked(self):
        self.mask_path = self.fileMngt.OpenDirectoryDialog()
        if self.mask_path == "":
            print("Choose mask fail!")
        else:
            self.ui.maskPath.setText(self.mask_path)

    def signalToAllFiles(self):
        if self.ui.allFilesButton.isChecked():
            self.allFilesSignal.emit()
        else:
            self.oneFileSignal.emit()

    def signalToExecute(self):
        self.executeSignal.emit()


class EditWidget(QWidget):
    selectSignal = pyqtSignal()
    rectangleSignal = pyqtSignal()
    ellipseSignal = pyqtSignal()
    freeshapeSignal = pyqtSignal()
    thicknessSignal = pyqtSignal(int)
    colorSignal = pyqtSignal(QColor)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Edit()
        self.ui.setupUi(self)

        self.lastColor = Qt.red

        self.ui.rectangleButton.clicked.connect(self.signalToRectangle)
        self.ui.ellipseButton.clicked.connect(self.signalToEllipse)
        self.ui.freeshapeButton.clicked.connect(self.signalToFreeshape)
        self.ui.thicknessBox.valueChanged.connect(self.signalToThickness)
        self.ui.colorButton.clicked.connect(self.openColorPicker)

    def signalToRectangle(self):
        if self.ui.rectangleButton.isChecked():
            self.ui.ellipseButton.setChecked(False)
            self.ui.freeshapeButton.setChecked(False)
            self.rectangleSignal.emit()
        else:
            self.selectSignal.emit()

    def signalToEllipse(self):
        if self.ui.ellipseButton.isChecked():
            self.ui.rectangleButton.setChecked(False)
            self.ui.freeshapeButton.setChecked(False)
            self.ellipseSignal.emit()
        else:
            self.selectSignal.emit()

    def signalToFreeshape(self):
        if self.ui.freeshapeButton.isChecked():
            self.ui.rectangleButton.setChecked(False)
            self.ui.ellipseButton.setChecked(False)
            self.freeshapeSignal.emit()
        else:
            self.selectSignal.emit()

    def signalToThickness(self):
        thickness = self.ui.thicknessBox.value()
        self.thicknessSignal.emit(thickness)

    def openColorPicker(self):
        color = QColorDialog.getColor(self.lastColor, self)
        if color.isValid():
            self.lastColor = color
            self.ui.colorLabel.setStyleSheet("QWidget {background-color: %s}" % color.name())
            self.colorSignal.emit(color)

class ReportMainWidget(QWidget):
    nextImageSignal = pyqtSignal()
    prevImageSignal = pyqtSignal()
    openReportSignal = pyqtSignal()
    showDiseaseSignal = pyqtSignal(bool)
    selectDiseaseSignal = pyqtSignal(str)
    selectedToReportSignal = pyqtSignal(bool)

    def __init__(self, config=None):
        super().__init__()
        self.ui = UiReportMain()
        self.ui.setupUi(self)

        self.ui.nextButton.clicked.connect(self.nextImageSignal)
        self.ui.prevButton.clicked.connect(self.prevImageSignal)
        self.ui.openReportButton.clicked.connect(self.openReportSignal)
        self.ui.showDiseaseCheckBox.setChecked(True)
        self.ui.showDiseaseCheckBox.toggled.connect(self.on_radio_button_toggled)
        self.ui.diseaseTypeComboBox.currentIndexChanged.connect(self.on_combobox_index_changed)
        self.ui.addToReportCheckBox.toggled.connect(self.on_selected_to_report_button_toggled)
        self.items = []

    def clearDisease(self):
        self.ui.diseaseTypeComboBox.clear()
        self.items = []
        
    def addDisease(self, item):
        self.items.append(item)
        self.ui.diseaseTypeComboBox.addItem(item)

    def on_radio_button_toggled(self):
        self.showDiseaseSignal.emit(self.ui.showDiseaseCheckBox.isChecked())
    
    def on_selected_to_report_button_toggled(self):
        self.selectedToReportSignal.emit(self.ui.addToReportCheckBox.isChecked())

    def on_combobox_index_changed(self, index):
        item = self.items[index]
        self.selectDiseaseSignal.emit(item)

class ReportSortWidget(QWidget):
    sortBySignal = pyqtSignal(str)

    def __init__(self, config=None):
        super().__init__()
        self.ui = Ui_ReportSort()
        self.ui.setupUi(self)
        self.ui.sortByName.setChecked(True)
        self.ui.sortByName.toggled.connect(self.on_radio_button_toggled)
        self.ui.sortByDate.toggled.connect(self.on_radio_button_toggled)
        self.ui.sortBySize.toggled.connect(self.on_radio_button_toggled)

    def on_radio_button_toggled(self):
        # Check which radio button is checked
        if self.ui.sortByName.isChecked():
            # print("buttonHoangLong selected")
            self.sortBySignal.emit('name')
        elif self.ui.sortByDate.isChecked():
            # print("buttonBHDHYselected")
            self.sortBySignal.emit('created_date')
        elif self.ui.sortBySize.isChecked():
            # print("buttonHaiDuongselected")
            self.sortBySignal.emit('size')
    
class ReportHospitalWidget(QWidget):
    selectHospitalSignal = pyqtSignal(str)

    def __init__(self, config=None):
        super().__init__()
        self.ui = Ui_Report()
        self.ui.setupUi(self)
        # self.ui.buttonHoangLong.setChecked(True)

        self.ui.buttonHoangLong.toggled.connect(self.on_radio_button_toggled)
        self.ui.buttonBHDHY.toggled.connect(self.on_radio_button_toggled)
        self.ui.buttonHaiDuong.toggled.connect(self.on_radio_button_toggled)

    def on_radio_button_toggled(self):
        # Check which radio button is checked
        if self.ui.buttonHoangLong.isChecked():
            # print("buttonHoangLong selected")
            self.selectHospitalSignal.emit('hl')
        elif self.ui.buttonBHDHY.isChecked():
            # print("buttonBHDHYselected")
            self.selectHospitalSignal.emit('dhy')
        elif self.ui.buttonHaiDuong.isChecked():
            # print("buttonHaiDuongselected")
            self.selectHospitalSignal.emit('hd')
