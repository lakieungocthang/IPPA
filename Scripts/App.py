import os
import json
from datetime import datetime
from PIL import Image

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import qdarktheme

from Resources.Gui.ui_app import *
from Scripts.Utils import *
from Scripts.File_Mngt import FileMngt
from Scripts.Image_Viewer import ImageViewer
from Scripts.ReconstructionViewer import PointCloudViewer
from Scripts.CollapseWidget import *
from Scripts.ReportUtils import *
from Scripts.MakeReport import *
from Scripts.Dicom import *
from Scripts.Classify import Classify
from Scripts.Detector import Detector
from Scripts.Generator import Generator
from Scripts.Tracker import Tracker
from Scripts.Reconstructor import Reconstructor
from Scripts.Image_Data import ImageData


class MainWindow(QMainWindow):
    images_data = []
    current_index = 0

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("My App")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        qdarktheme.setup_theme("dark")
        self.load_stylesheet()
        self.config = self.load_config('config.json')

        self.fileMngt = FileMngt()

        self.image = QPixmap()
        self.ui.stackedWidget.setCurrentIndex(1)

        self.SetupToolbar()
        self.SetupDockers()
        self.SetupMenutree()
        self.SetupImageViewer()
        self.SetupReconstructionViewer()
        self.SetupTransform()
        self.SetupEdit()
        self.SetupReport()
        self.SetupExportDicom()
        self.SetupClassify()
        self.SetupDetector()
        self.SetupGenerator()
        self.SetupTracker()
        self.SetupReconstructor()

    def load_stylesheet(self):
        with open('./Resources/Themes_Script/Custom.qss', 'r') as f:
            stylesheet = f.read()
            self.setStyleSheet(stylesheet)
    
    def load_config(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        else:
            return {}

# ==========================================Set up=======================================================
# ------------------------------------------Set up toolbar--------------------------------------------------

    def SetupToolbar(self):
        self.ActionsTrigger()
        logo = QLabel(self)
        logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pixmap = QPixmap("./Resources/NewIcons/logo.jpg")
        logo_pixmap = pixmap.scaledToHeight(104, Qt.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        self.ui.toolBar_4.addWidget(logo)

    def ActionsTrigger(self):
        self.ui.actionOpen_Folder.triggered.connect(self.OnOpenFolderTrigger)
        self.ui.actionTransform.triggered.connect(self.OnTransformTrigger)
        self.ui.actionEdit.triggered.connect(self.OnEditTrigger)
        self.ui.actionReport.triggered.connect(self.HideOtherDockers)
        self.ui.actionReport.triggered.connect(self.OnReportTrigger)
        self.ui.actionClassify.triggered.connect(self.OnClassifyTrigger)
        self.ui.actionDetector.triggered.connect(self.OnDetectorTrigger)
        self.ui.actionGenerate.triggered.connect(self.OnGeneratorTrigger)
        self.ui.actionTracking.triggered.connect(self.OnTrackerTrigger)
        self.ui.actionReconstruct.triggered.connect(self.OnReconstructTrigger)
        self.ui.actionExport.triggered.connect(self.OnExportTrigger)
        self.ui.actionSave.triggered.connect(self.OnSaveTrigger)
        self.ui.actionReset.triggered.connect(self.OnResetTrigger)

    def OnOpenFolderTrigger(self):
        lst_file_path = self.fileMngt.LoadFolder()
        self.ui.dockHierarchy.show()
        self.LoadData(lst_file_path)
        self.LoadTreeView()

    def OnTransformTrigger(self, p_status):
        if p_status:
            self.ui.LayoutTransform.addWidget(self.transform)
            self.ui.dockTransform.show()
            self.ui.dockTransform.raise_()
        else:
            self.ui.dockTransform.hide()

    def OnEditTrigger(self, p_status):
        if p_status:
            self.ui.LayoutEdit.addWidget(self.edit)
            self.ui.dockEdit.show()
            self.ui.dockEdit.raise_()
        else:
            self.ui.dockEdit.hide()

    def OnClassifyTrigger(self, p_status):
        if p_status:
            self.ui.LayoutClassify.addWidget(self.classify)
            self.ui.dockClassify.show()
            self.ui.dockClassify.raise_()
        else:
            self.ui.dockClassify.hide()

    def OnDetectorTrigger(self, p_status):
        if p_status:
            self.ui.LayoutDetector.addWidget(self.detector)
            self.ui.dockDetector.show()
            self.ui.dockDetector.raise_()
        else:
            self.ui.dockDetector.hide()

    def OnGeneratorTrigger(self, p_status):
        if p_status:
            self.ui.LayoutGenerator.addWidget(self.generator)
            self.ui.dockGenerator.show()
            self.ui.dockGenerator.raise_()
        else:
            self.ui.dockGenerator.hide()

    def OnTrackerTrigger(self, p_status):
        if p_status:
            self.ui.LayoutTracker.addWidget(self.tracker)
            self.ui.dockTracker.show()
            self.ui.dockTracker.raise_()
        else:
            self.ui.dockTracker.hide()

    def OnExportTrigger(self):
        image_data = self.images_data[self.current_index]
        self.ExportDicomFile(image_data)

    def OnSaveTrigger(self):
        data = self.images_data[self.current_index]
        self.fileMngt.SaveData(data)

    def OnResetTrigger(self):
        self.image = self.images_data[self.current_index].original_image
        self.UpdateImageViewer(self.image)

    def OnReconstructTrigger(self, p_status):
        if p_status:
            self.ui.LayoutReconstructor.addWidget(self.reconstructor)
            self.ui.dockReconstructor.show()
            self.ui.dockReconstructor.raise_()
            self.ui.stackedWidget.setCurrentIndex(0)
            self.UpdateDisplayMask()
            self.ui.treeView.clicked.connect(self.UpdateDisplayMask)
        else:
            self.ui.treeView.clicked.disconnect(self.UpdateDisplayMask)
            self.ui.dockReconstructor.hide()
            self.ui.stackedWidget.setCurrentIndex(1)

    def OnWidthChanged(self):
        self.widthChanged = True
        self.heightChanged = False

    def OnHeightChanged(self):
        self.heightChanged = True
        self.widthChanged = False

    def OnRatioCheck(self):
        self.transform.executeSignal.disconnect(self.IgnoreRatioResize)
        self.transform.executeSignal.connect(self.KeepRatioResize)

    def OnRatioUncheck(self):
        self.transform.executeSignal.disconnect(self.KeepRatioResize)
        self.transform.executeSignal.connect(self.IgnoreRatioResize)

    def IgnoreRatioResize(self):
        newWidth = self.transform.ui.widthBox.value()
        newHeight = self.transform.ui.heightBox.value()
        self.imageViewer.ResizeIgnoreRatio(QSize(newWidth, newHeight))

    def KeepRatioResize(self):
        if self.widthChanged:
            newWidth = self.transform.ui.widthBox.value()
            self.imageViewer.ResizeToWidth(newWidth)
        elif self.heightChanged:
            newHeight = self.transform.ui.heightBox.value()
            self.imageViewer.ResizeToHeight(newHeight)

    def CropImage(self):
        self.imageViewer.Crop()

    def OnCropCheck(self):
        self.edit.ui.rectangleButton.setChecked(False)
        self.edit.ui.ellipseButton.setChecked(False)
        self.edit.ui.freeshapeButton.setChecked(False)
        self.imageViewer.SetDrawMode("crop")
        if self.transform.ui.ratioButton.isChecked():
            self.transform.executeSignal.disconnect(self.KeepRatioResize)
        else:
            self.transform.executeSignal.disconnect(self.IgnoreRatioResize)
        self.transform.executeSignal.connect(self.CropImage)

    def OnCropUncheck(self):
        self.imageViewer.SetDrawMode(None)
        self.transform.executeSignal.disconnect(self.CropImage)
        if self.transform.ui.ratioButton.isChecked():
            self.transform.executeSignal.connect(self.KeepRatioResize)
        else:
            self.transform.executeSignal.connect(self.IgnoreRatioResize)

    def OnTypeUncheck(self):
        self.imageViewer.SetDrawMode(None)

    def OnRectangleClick(self):
        self.transform.ui.cropButton.setChecked(False)
        self.imageViewer.SetDrawMode("rectangle")

    def OnEllipseClick(self):
        self.transform.ui.cropButton.setChecked(False)
        self.imageViewer.SetDrawMode("ellipse")

    def OnFreeshapeClick(self):
        self.transform.ui.cropButton.setChecked(False)
        self.imageViewer.SetDrawMode("free_style")

# ------------------------------------------Set up docker--------------------------------------------------

    def SetupDockers(self):
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockTransform)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockEdit)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockClassify)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockDetector)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockGenerator)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockTracker)
        # self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockReport)
        self.tabifyDockWidget(self.ui.dockProperties, self.ui.dockReconstructor)
        self.ui.dockReportHeader.hide()
        self.ui.dockReportHeader2.hide()
        self.ui.dockReportMain.hide()
        self.ui.dockHierarchyReport.hide()
        self.ui.dockHierarchy.hide()
        self.ui.dockProperties.hide()
        self.ui.dockTransform.hide()
        self.ui.dockEdit.hide()
        self.ui.dockClassify.hide()
        self.ui.dockDetector.hide()
        self.ui.dockGenerator.hide()
        self.ui.dockTracker.hide()
        self.ui.dockReconstructor.hide()
        self.ui.dockReport.hide()

    def SetupTransform(self):
        self.transform = TransformWidget()
        self.transform.cropSignal.connect(self.OnCropCheck)
        self.transform.noCropSignal.connect(self.OnCropUncheck)
        self.transform.keepRatioSignal.connect(self.OnRatioCheck)
        self.transform.ignoreRatioSignal.connect(self.OnRatioUncheck)
        self.transform.executeSignal.connect(self.IgnoreRatioResize)
        self.transform.widthChangedSignal.connect(self.OnWidthChanged)
        self.transform.heightChangedSignal.connect(self.OnHeightChanged)

    def SetupEdit(self):
        self.edit = EditWidget()
        self.edit.selectSignal.connect(self.OnTypeUncheck)
        self.edit.rectangleSignal.connect(self.OnRectangleClick)
        self.edit.ellipseSignal.connect(self.OnEllipseClick)
        self.edit.freeshapeSignal.connect(self.OnFreeshapeClick)
        self.edit.thicknessSignal.connect(self.imageViewer.SetThickness)
        self.edit.colorSignal.connect(self.imageViewer.SetColor)

    # region Report Functions
    def HideOtherDockers(self):
        self.OnClassifyTrigger(False)
        self.OnDetectorTrigger(False)
        self.OnGeneratorTrigger(False)
        self.OnTrackerTrigger(False)
        self.OnTransformTrigger(False)
        self.OnEditTrigger(False)
        self.OnReconstructTrigger(False)

    def DiableOtherActions(self):
        self.ui.actionTransform.setEnabled(False)
        self.ui.actionEdit.setEnabled(False)
        self.ui.actionClassify.setEnabled(False)
        self.ui.actionDetector.setEnabled(False)
        self.ui.actionGenerate.setEnabled(False)
        self.ui.actionTracking.setEnabled(False)
        self.ui.actionReconstruct.setEnabled(False)

        self.ui.actionTransform.setChecked(False)
        self.ui.actionEdit.setChecked(False)
        self.ui.actionClassify.setChecked(False)
        self.ui.actionDetector.setChecked(False)
        self.ui.actionGenerate.setChecked(False)
        self.ui.actionTracking.setChecked(False)
        self.ui.actionReconstruct.setChecked(False)

    def EnableOtherActions(self):
        self.ui.actionTransform.setEnabled(True)
        self.ui.actionEdit.setEnabled(True)
        self.ui.actionClassify.setEnabled(True)
        self.ui.actionDetector.setEnabled(True)
        self.ui.actionGenerate.setEnabled(True)
        self.ui.actionTracking.setEnabled(True)
        self.ui.actionReconstruct.setEnabled(True)
    
    def OnReportTrigger(self, p_status):
        if p_status:
            self.DiableOtherActions()
            # self.setCentralWidget(self.report)

            # self.ui.stackedWidget.addWidget(self.report)
            # self.ui.centralwidget.addWidget(self.report)
            # self.ui.centralwidget.show()
            self.ui.centralwidget.hide()

            # self.ui.centralwidget.raise_()
            # self.ui.L.addWidget(self.report)

            self.ui.dockHierarchyReport.setMinimumWidth(300)
            self.ui.dockHierarchyReport.setMaximumWidth(500)
            # self.ui.dockReportHeader.setMinimumWidth(300)
            # self.ui.dockReportHeader2.setMinimumWidth(300)
            # self.ui.dockReportHeader.setMinimumWidth(150)
            # self.ui.dockReportHeader2.setMinimumWidth(100)
            # self.ui.dockHierarchy.setGeometry(self.ui.dockHierarchy.geometry().adjusted(0, 0, 50, 0))
            # self.ui.dockReportHeader2.setGeometry(self.ui.dockReportHeader2.geometry().adjusted(0, 0, 50, 0))
            # self.ui.dockReportHeader.setGeometry(self.ui.dockReportHeader.geometry().adjusted(0, 0, 50, 0))
            
            # self.ui.dockHierarchy.setGeometry(self.ui.dockHierarchy.geometry().adjusted(0, 0, 200, 0))
            self.ui.dockHierarchyReport.show()
            self.ui.dockHierarchy.hide()
            self.ui.dockProperties.hide()

            

            self.ui.LayoutReportHeader.addWidget(self.reportHospital)
            
            self.ui.LayoutReportHeader2.addWidget(self.reportSort)
            self.ui.LayoutReportMain.addWidget(self.reportMain)

            self.ui.dockReportHeader.setMinimumHeight(200)
            self.ui.dockReportHeader.setMaximumHeight(300)
            self.ui.dockReportHeader2.setMinimumHeight(150)
            self.ui.dockReportHeader2.setMaximumHeight(250)

            self.ui.dockReportHeader.show()
            self.ui.dockReportHeader2.show()
            self.ui.dockReportMain.show()


            # self.ui.centralwidget.show()
            # self.ui.dockClassify.show()
            # self.ui.dockClassify.raise_()
        else:
            self.EnableOtherActions()
            self.ui.dockReportHeader.hide()
            self.ui.dockReportHeader2.hide()
            self.ui.dockReportMain.hide()
            self.ui.dockHierarchyReport.hide()
            self.ui.centralwidget.show()
            self.ui.dockHierarchy.show()
            self.ui.dockProperties.show()

            # self.setCentralWidget(self.ui.centralwidget)
            # self.ui.dockEdit.hide()
    def SetupReport(self):

        self.reportHospital = ReportHospitalWidget(self.config)
        self.reportSort = ReportSortWidget(self.config)
        self.reportMain = ReportMainWidget(self.config)
        self.sortCode = 'name'


        self.imageViewerReport = ImageViewer()
        # layout = QBoxLayout(self.reportMain.ui.imageViewerWidget)
        # layout.addWidget(self.imageViewerReport)
        self.reportMain.ui.imageViewerWidget.setLayout(QVBoxLayout())  # Ensure the widget has a layout
        self.reportMain.ui.imageViewerWidget.layout().addWidget(self.imageViewerReport)
        
        # self.reportMain.ui.imageGraphicLayout.addWidget(self.imageViewerReport)
        self.imageViewerReport.updatedImageSignal.connect(self.UpdateReportImage)
        
        self.imageViewerReport.ResetZoom()

        self.reportModel = QStandardItemModel()
        self.reportModel.setHorizontalHeaderLabels(['Index', 'Folder name', 'Size','Images'])
        self.ui.treeViewReport.setModel(self.reportModel)

        self.reportHospital.selectHospitalSignal.connect(self.OnHospitalClick)
        self.reportMain.nextImageSignal.connect(self.OnNextReportImageClick)
        self.reportMain.prevImageSignal.connect(self.OnPrevReportImageClick)
        self.reportMain.openReportSignal.connect(self.OnOpenReportClick)
        self.reportMain.showDiseaseSignal.connect(self.OnShowDiseaseClick)
        self.reportMain.selectedToReportSignal.connect(self.OnSelectedToReportClick)
        self.reportMain.selectDiseaseSignal.connect(self.OnSelectDiseaseClick)
        self.reportSort.sortBySignal.connect(self.OnReportSort)


        
        self.showDisease = True
        self.diseaseType = 'all'
        self.reportPhotoIndex = 0
        # self.edit = EditWidget()
        # self.edit.selectSignal.connect(self.OnSelectClick)
        # self.edit.ellipseSignal.connect(self.OnEllipseClick)
        # self.edit.freeshapeSignal.connect(self.OnFreeshapeClick)
        # self.edit.thicknessSignal.connect(self.imageViewer.SetThickness)
        # self.edit.colorSignal.connect(self.imageViewer.SetColor)
    
    def OnHospitalClick(self, code: str):
        hospitals =  self.config['report']['hospitals']
        for hospital in hospitals:
            if hospital['code'] == code:
                folder = hospital['folder']
                self.hospitalCode = code
                self.hospitalDir = folder
                self.OnLoadReports(folder)

    def OnReportSort(self, code):
        self.sortCode = code
        self.reportFolders = sort_folders(self.hospital_dir, code)
        self.UpdateReportFolder()

    def OnLoadReports(self, hospital_dir: str):
        self.hospital_dir = hospital_dir
        self.reportFolders = sort_folders(hospital_dir, self.sortCode)
        if len(self.reportFolders) > 0:
            self.reportFolder = self.reportFolders[0]
        self.UpdateReportFolder()
        
    
    def UpdateReportFolder(self):
        try:
            self.ui.treeViewReport.clicked.disconnect(self.ChooseReportDate)
        except: pass
        try:
            self.ui.treeViewReport.clicked.disconnect(self.ChooseReportPhoto)
        except: pass

        if self.reportModel.rowCount() > 0:
            self.reportModel.clear()
            self.reportModel.setHorizontalHeaderLabels(['Index', 'Folder Name', 'Size','Images'])
        for i,folder in enumerate(self.reportFolders):
            index_item = QStandardItem(str(i+1))
            name = QStandardItem(folder.name)
            size = QStandardItem(convert_size(folder.size))
            imagesCount = QStandardItem(str(len(folder.images)))
            self.reportModel.appendRow([index_item, name, size, imagesCount])
        self.ui.treeViewReport.clicked.connect(self.ChooseReportDate)
    
    def UpdateReportImages(self, index):
        # print ("i8ndex",len(self.reportFolders), index)
        self.reportFolder = self.reportFolders[index]
        try:
            self.ui.treeViewReport.clicked.disconnect(self.ChooseReportDate)
        except: pass
        if self.reportModel.rowCount() > 0:
            self.reportModel.clear()
            self.reportModel.setHorizontalHeaderLabels(['Index', 'Image','Selected','Diseases'])
        self.reportModel.appendRow([QStandardItem(''),QStandardItem('(Go Back)'),QStandardItem(''),QStandardItem('')])
        for i,image in enumerate(self.reportFolder.images):
            image.parse_yaml()
            index_item = QStandardItem(str(i+1))
            name = QStandardItem(image.base_name)
            selected = QStandardItem('Y' if image.selected  else '')
            diseases = QStandardItem(image.get_short_label())
            # selected = QStandardItem(str(image.selected))
            # size = QStandardItem(convert_size(folder.size))
            # imagesCount = QStandardItem(str(len(folder.images)))
            self.reportModel.appendRow([index_item, name, selected, diseases])
        self.ui.treeViewReport.clicked.connect(self.ChooseReportPhoto)

    def UpdateReportImage(self, p_image):
        self.image = p_image


    def ChooseReportDate(self, item: QModelIndex):
        id = max(item.row(),0)
        self.ReportFolderIndex = id
        self.UpdateReportImages(id)
    
    
    def OnNextReportImageClick(self):
        maxLen = len(self.reportFolder.images)
        self.reportPhotoIndex = min(maxLen-1,self.reportPhotoIndex+1)
        self.UpdateReportPhoto()

    def OnPrevReportImageClick(self):
        self.reportPhotoIndex = max(0,self.reportPhotoIndex-1)
        self.UpdateReportPhoto()
        
    def OnOpenReportClick(self):
        make_report(self.reportFolder,self.config['report'], self.hospitalCode)
    
    def OnShowDiseaseClick(self, show):
        self.showDisease = show
        self.UpdateReportDisplay()
    def OnSelectedToReportClick(self, selected):
        
        if self.image_obj is not None:
            if self.image_obj in self.reportFolder.images:
                index = self.reportFolder.images.index(self.image_obj) + 1
                # row[2] = QStandardItem('Y' if selected  else '')
                self.reportModel.setItem(index, 2 ,QStandardItem('Y' if selected  else ''))
            self.image_obj.selected = selected
            self.image_obj.save_yaml()
    
    def OnSelectDiseaseClick(self, disease):
        self.diseaseType = disease
        self.UpdateReportDisplay()

    def UpdateReportDisplay(self):
        self.imageViewerReport.SetImage(self.pixmapReport)
        self.imageViewerReport.DisplayImage()
        if self.showDisease:
            for box in self.image_obj.boxes:
                if box.label == self.diseaseType or self.diseaseType == 'all':
                    self.imageViewerReport.DrawBox(box.pt1, box.pt2, box.label)

    def UpdateReportPhoto(self):
        
        self.image_obj = self.reportFolder.images[self.reportPhotoIndex]
        self.pixmapReport = QPixmap(self.image_obj.file_path)
        # self.image = pixmap
        # self.setCentralWidget(self.imageViewerReport)
        # self.imageViewerReport
        self.imageViewerReport.SetImage(self.pixmapReport)
        self.imageViewerReport.DisplayImage()
        # self.reportMain.ui.showDiseaseCheckBox.setChecked(True)



        index = self.reportModel.index(self.reportPhotoIndex+1, 0)
        selection_model = self.ui.treeViewReport.selectionModel()
        selection_model.clearSelection()
        selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.image_obj.parse_yaml()
        self.reportMain.ui.addToReportCheckBox.setChecked(self.image_obj.selected)
        for box in self.image_obj.boxes:
            self.imageViewerReport.DrawBox(box.pt1, box.pt2, box.label)
        self.reportMain.clearDisease()
        self.reportMain.addDisease('all')
        for label in self.image_obj.label_dict.keys():
            self.reportMain.addDisease(label)
            # self.diseaseType = label
            
    

    def ChooseReportPhoto(self, item: QModelIndex):
        id = max(item.row(),0)
        if id==0:
            try:
                self.ui.treeViewReport.clicked.disconnect(self.ChooseReportPhoto)
            except: pass
            self.UpdateReportFolder()
        else:
            self.reportPhotoIndex = id-1
            self.UpdateReportPhoto()
    # endregion

# ------------------------------------------Set up menutree--------------------------------------------------

    def SetupMenutree(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Index', 'File name', 'Type'])
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.expandAll()
        self.ui.treeView.setColumnWidth(0, 50)

        self.ui.treeView.clicked.connect(self.ChooseImage)

    def ChooseImage(self, p_index: QModelIndex):
        self.current_index = p_index.row()
        file_path = self.images_data[self.current_index].information["path"]

        info, width, height = self.GetImageInfo(file_path)
        self.ui.labelProperties.setText(info)
        self.UpdateSize(width, height)

        pixmap = QPixmap(file_path)
        self.images_data[self.current_index].original_image = pixmap

        self.image = pixmap
        self.UpdateImageViewer(pixmap)

    def LoadTreeView(self):
        self.ClearTreeView()
        self.DisplayDockProperties()
        for m_image_data in self.images_data:
            index_item = QStandardItem(str(m_image_data.information["id"]))
            name_item = QStandardItem(m_image_data.information["name"])
            type_item = QStandardItem(m_image_data.information["type"])
            self.model.appendRow([index_item, name_item, type_item])

    def ClearTreeView(self):
        if self.model.rowCount() > 0:
            self.model.clear()
            self.model.setHorizontalHeaderLabels(
                ['Index', 'File name', 'Type'])

    def DisplayDockProperties(self):
        self.ui.dockProperties.show()
        self.ui.dockProperties.raise_()

# ------------------------------------------Set up imageviewer--------------------------------------------------

    def SetupImageViewer(self):
        self.imageViewer = ImageViewer()
        self.ui.imageGraphicLayout.addWidget(self.imageViewer)
        self.imageViewer.updatedImageSignal.connect(self.UpdateCurrentImage)
        self.imageViewer.sizeSignal.connect(self.UpdateSize)

    def UpdateImageViewer(self, p_image):
        self.imageViewer.SetImage(p_image)
        self.imageViewer.DisplayImage()

    def UpdateSize(self, p_width, p_height):
        self.transform.ui.widthBox.setValue(p_width)
        self.transform.ui.heightBox.setValue(p_height)

# ------------------------------------------Set up reconstruct viewer--------------------------------------------------

    def SetupReconstructionViewer(self):
        self.reconstructionViewer = PointCloudViewer()
        self.ui.image3dLayout.addWidget(self.reconstructionViewer)

# ==========================================Setup Classify=======================================================

    def SetupClassify(self):
        self.classify = Classify()
        self.classify.updateOutputImageSignal.connect(self.UpdateCurrentImage)
        self.classify.updateOutputImageSignal.connect(self.UpdateImageViewer)
        self.classify.updateClassifyResult.connect(self.UpdateClassifyResult)
        self.classify.requestUpdateImage.connect(self.UpdateClassify)
        self.classify.requestImagesList.connect(self.UpdateClassifyImageList)

    def UpdateClassify(self):
        self.classify.SetInputImage(self.image)

    def UpdateClassifyImageList(self):
        images_path_list = []
        for item in self.images_data:
            images_path_list.append(item.information["path"])
        self.classify.SetImagesList(images_path_list)

    def UpdateClassifyResult(self, p_data):
        self.images_data[self.current_index].classify["land-mark"] = p_data[0]
        self.images_data[self.current_index].classify_image = p_data[1]

# ==========================================Setup Detection=======================================================

    def SetupDetector(self):
        self.detector = Detector()
        self.detector.updateOutputImageSignal.connect(self.UpdateCurrentImage)
        self.detector.updateOutputImageSignal.connect(self.UpdateImageViewer)
        self.detector.updateDetectionResult.connect(self.UpdateDetectionResult)
        self.detector.requestUpdateImage.connect(self.UpdateDetector)
        self.detector.requestImagesList.connect(self.UpdateDetectorImageList)

    def UpdateDetector(self):
        self.detector.SetInputImage(self.image)

    def UpdateDetectorImageList(self):
        images_path_list = []
        for item in self.images_data:
            images_path_list.append(item.information["path"])
        self.detector.SetImagesList(images_path_list)

    def UpdateDetectionResult(self, p_data):
        self.images_data[self.current_index].detector["num-lesion"] = p_data[0]
        self.images_data[self.current_index].detector_image = p_data[1]
        self.images_data[self.current_index].detector["lesion-data"] = p_data[2]

    # ==========================================Setup Generator=======================================================

    def SetupGenerator(self):
        self.generator = Generator()
        self.generator.updateOutputImageSignal.connect(self.UpdateCurrentImage)
        self.generator.updateOutputImageSignal.connect(self.UpdateImageViewer)
        self.generator.updateGeneratorFiceResult.connect(
            self.UpdateGeneratorFiceResult)
        self.generator.updateGeneratorLciResult.connect(
            self.UpdateGeneratorLciResult)
        self.generator.requestUpdateImage.connect(self.UpdateGenerator)

    def UpdateGenerator(self):
        self.generator.SetInputImage(self.image)

    def UpdateGeneratorFiceResult(self, p_data):
        self.images_data[self.current_index].generator["FICE"] = "True"
        self.images_data[self.current_index].fice_image = p_data[0]

    def UpdateGeneratorLciResult(self, p_data):
        self.images_data[self.current_index].generator["LCI"] = "True"
        self.images_data[self.current_index].lci_image = p_data[0]

# ==========================================Setup Tracking=======================================================

    def SetupTracker(self):
        self.tracker = Tracker()
        self.tracker.updateOutputImageSignal.connect(self.UpdateCurrentImage)
        self.tracker.updateOutputImageSignal.connect(self.UpdateImageViewer)
        self.tracker.requestUpdateImage.connect(self.UpdateTracker)

    def UpdateTracker(self):
        self.tracker.SetInputImage(self.image)

# ==========================================Setup Reconstructor=======================================================

    def SetupReconstructor(self):
        self.reconstructor = Reconstructor()
        self.reconstructor.updateReconstructorResult.connect(self.UpdateReconstructorResult)
        self.reconstructor.requestUpdateImage.connect(self.UpdateReconstructor)

    def UpdateReconstructor(self):
        # self.reconstructionViewer.clear()
        self.reconstructor.SetInputImage(self.image)

    def UpdateDisplayMask(self):
        self.reconstructor.UpdateDisplayMask(self.image)

    def UpdateReconstructorResult(self, p_data):
        self.reconstructionViewer.Initialize()
        self.reconstructionViewer.load_and_plot_point_cloud(p_data[0], p_data[1])

    # ==========================================Setup Export Dicom=======================================================

    def SetupExportDicom(self):
        self.exportDicom = Dicom()

    def ExportDicomFile(self, p_data):
        save_dicom_dir = self.fileMngt.OpenDirectoryDialog()
        file_name = os.path.splitext(self.images_data[self.current_index].information["name"])[0]
        save_dicom_path = os.path.join(save_dicom_dir, file_name)
        self.exportDicom.SaveDicomFile(save_dicom_path, p_data)

    # ==========================================Key events=======================================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Alt:
            self.imageViewer.altPressedEvent(True)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt:
            self.imageViewer.altPressedEvent(False)
        super().keyReleaseEvent(event)

# ==========================================Body=======================================================

    def UpdateCurrentImage(self, p_image):
        self.image = p_image

    def LoadData(self, lst_file_path):
        self.images_data = []
        i = 0
        for file_path in lst_file_path:
            image_data = ImageData()
            file_name = os.path.basename(file_path)
            image_data.information["id"] = i
            image_data.information["name"] = file_name
            image_data.information["path"] = file_path
            image_data.information["type"] = os.path.splitext(file_name)[1]
            image_data.original_image = QPixmap()  # None value if that image not change
            self.images_data.append(image_data)
            i += 1

    def GetImageInfo(self, p_file_path):
        image = Image.open(p_file_path)
        file_name = os.path.basename(p_file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        mod_time = os.path.getmtime(p_file_path)
        mod_date = datetime.fromtimestamp(
            mod_time).strftime('%Y-%m-%d %H:%M:%S')
        width, height = image.size
        color_mode = image.mode

        info = f"""Location: {file_name}
Type: {file_extension}
Color Mode: {color_mode}
Creation Date: {mod_date}
Dimensions: {width} x {height}"""
        return info, width, height
