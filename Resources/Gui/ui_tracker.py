# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tracker.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Tracker(object):
    def setupUi(self, Tracker):
        Tracker.setObjectName("Tracker")
        Tracker.resize(442, 428)
        self.trackLayout = QtWidgets.QVBoxLayout(Tracker)
        self.trackLayout.setObjectName("trackLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Tracker)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.trackResult = QtWidgets.QLineEdit(Tracker)
        self.trackResult.setObjectName("trackResult")
        self.horizontalLayout_2.addWidget(self.trackResult)
        self.trackLayout.addLayout(self.horizontalLayout_2)
        self.listWidget = QtWidgets.QListWidget(Tracker)
        self.listWidget.setObjectName("listWidget")
        self.trackLayout.addWidget(self.listWidget)

        self.retranslateUi(Tracker)
        QtCore.QMetaObject.connectSlotsByName(Tracker)

    def retranslateUi(self, Tracker):
        _translate = QtCore.QCoreApplication.translate
        Tracker.setWindowTitle(_translate("Tracker", "Form"))
        self.label_2.setText(_translate("Tracker", "Num lesion"))
