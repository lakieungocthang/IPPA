# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\reportMain.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class UiReportMain(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1467, 1232)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.topLeftLayout = QtWidgets.QHBoxLayout()
        self.topLeftLayout.setObjectName("topLeftLayout")
        self.addToReportCheckBox = QtWidgets.QCheckBox(Form)
        # self.addToReportCheckBox.setChecked(True)
        self.addToReportCheckBox.setObjectName("addToReportCheckBox")
        self.topLeftLayout.addWidget(self.addToReportCheckBox)
        self.showDiseaseCheckBox = QtWidgets.QCheckBox(Form)
        self.showDiseaseCheckBox.setObjectName("showDiseaseCheckBox")
        self.topLeftLayout.addWidget(self.showDiseaseCheckBox)
        self.diseaseTypeComboBox = QtWidgets.QComboBox(Form)
        self.diseaseTypeComboBox.setProperty("items", ['Disease 1', 'Disease 2', 'Disease 3'])
        self.diseaseTypeComboBox.setObjectName("diseaseTypeComboBox")
        self.topLeftLayout.addWidget(self.diseaseTypeComboBox)
        self.gridLayout.addLayout(self.topLeftLayout, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.prevButton = QtWidgets.QPushButton(Form)
        self.prevButton.setObjectName("prevButton")
        self.horizontalLayout.addWidget(self.prevButton)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.imageViewerWidget = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageViewerWidget.sizePolicy().hasHeightForWidth())
        self.imageViewerWidget.setSizePolicy(sizePolicy)
        self.imageViewerWidget.setObjectName("imageViewerWidget")
        self.verticalLayout.addWidget(self.imageViewerWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.nextButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout.addWidget(self.nextButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.bottomRightLayout = QtWidgets.QHBoxLayout()
        self.bottomRightLayout.setObjectName("bottomRightLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.bottomRightLayout.addItem(spacerItem)
        self.openReportButton = QtWidgets.QPushButton(Form)
        self.openReportButton.setObjectName("openReportButton")
        self.bottomRightLayout.addWidget(self.openReportButton)
        self.gridLayout.addLayout(self.bottomRightLayout, 2, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.addToReportCheckBox.setText(_translate("Form", "Add to report"))
        self.showDiseaseCheckBox.setText(_translate("Form", "Show Disease"))
        self.prevButton.setText(_translate("Form", "<"))
        self.nextButton.setText(_translate("Form", ">"))
        self.openReportButton.setText(_translate("Form", "Open Report"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
