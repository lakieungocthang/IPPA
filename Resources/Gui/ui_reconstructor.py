# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reconstructor.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Reconstructor(object):
    def setupUi(self, Reconstructor):
        Reconstructor.setObjectName("Reconstructor")
        Reconstructor.resize(436, 528)
        self.reconstructorLayout = QtWidgets.QVBoxLayout(Reconstructor)
        self.reconstructorLayout.setObjectName("reconstructorLayout")
        self.reconstructorMask = QtWidgets.QLabel(Reconstructor)
        self.reconstructorMask.setText("")
        self.reconstructorMask.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstructorMask.setObjectName("reconstructorMask")
        self.reconstructorLayout.addWidget(self.reconstructorMask)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.reconstructorLayout.addItem(spacerItem)

        self.retranslateUi(Reconstructor)
        QtCore.QMetaObject.connectSlotsByName(Reconstructor)

    def retranslateUi(self, Reconstructor):
        _translate = QtCore.QCoreApplication.translate
        Reconstructor.setWindowTitle(_translate("Reconstructor", "Form"))
