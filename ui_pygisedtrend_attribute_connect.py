# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_pygisedtrend_attribute_connect.ui'
#
# Created: Sun Sep 28 09:51:10 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_pygisedtrend_attribute_connect(object):
    def setupUi(self, pygisedtrend_attribute_connect):
        pygisedtrend_attribute_connect.setObjectName(_fromUtf8("pygisedtrend_attribute_connect"))
        pygisedtrend_attribute_connect.resize(461, 285)
        self.buttonBox = QtGui.QDialogButtonBox(pygisedtrend_attribute_connect)
        self.buttonBox.setGeometry(QtCore.QRect(110, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.textEditLinksList = QtGui.QTextEdit(pygisedtrend_attribute_connect)
        self.textEditLinksList.setEnabled(False)
        self.textEditLinksList.setGeometry(QtCore.QRect(10, 90, 441, 151))
        self.textEditLinksList.setObjectName(_fromUtf8("textEditLinksList"))
        self.layoutWidget = QtGui.QWidget(pygisedtrend_attribute_connect)
        self.layoutWidget.setGeometry(QtCore.QRect(318, 21, 131, 52))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.labelGstaAttribute = QtGui.QLabel(self.layoutWidget)
        self.labelGstaAttribute.setObjectName(_fromUtf8("labelGstaAttribute"))
        self.verticalLayout_2.addWidget(self.labelGstaAttribute)
        self.comboGstaAttributeList = QtGui.QComboBox(self.layoutWidget)
        self.comboGstaAttributeList.setObjectName(_fromUtf8("comboGstaAttributeList"))
        self.comboGstaAttributeList.addItem(_fromUtf8(""))
        self.comboGstaAttributeList.addItem(_fromUtf8(""))
        self.comboGstaAttributeList.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.comboGstaAttributeList)
        self.layoutWidget1 = QtGui.QWidget(pygisedtrend_attribute_connect)
        self.layoutWidget1.setGeometry(QtCore.QRect(12, 21, 141, 52))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelShapeAttribute = QtGui.QLabel(self.layoutWidget1)
        self.labelShapeAttribute.setObjectName(_fromUtf8("labelShapeAttribute"))
        self.verticalLayout.addWidget(self.labelShapeAttribute)
        self.comboShapeAttributeList = QtGui.QComboBox(self.layoutWidget1)
        self.comboShapeAttributeList.setObjectName(_fromUtf8("comboShapeAttributeList"))
        self.verticalLayout.addWidget(self.comboShapeAttributeList)
        self.layoutWidget2 = QtGui.QWidget(pygisedtrend_attribute_connect)
        self.layoutWidget2.setGeometry(QtCore.QRect(160, 30, 151, 44))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Add = QtGui.QPushButton(self.layoutWidget2)
        self.Add.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/pygisedtrend/down.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Add.setIcon(icon)
        self.Add.setIconSize(QtCore.QSize(32, 32))
        self.Add.setObjectName(_fromUtf8("Add"))
        self.horizontalLayout.addWidget(self.Add)
        self.Del = QtGui.QPushButton(self.layoutWidget2)
        self.Del.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/pygisedtrend/up.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Del.setIcon(icon1)
        self.Del.setIconSize(QtCore.QSize(32, 32))
        self.Del.setObjectName(_fromUtf8("Del"))
        self.horizontalLayout.addWidget(self.Del)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButtonClearList = QtGui.QPushButton(pygisedtrend_attribute_connect)
        self.pushButtonClearList.setGeometry(QtCore.QRect(10, 250, 98, 27))
        self.pushButtonClearList.setObjectName(_fromUtf8("pushButtonClearList"))

        self.retranslateUi(pygisedtrend_attribute_connect)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), pygisedtrend_attribute_connect.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), pygisedtrend_attribute_connect.reject)
        QtCore.QMetaObject.connectSlotsByName(pygisedtrend_attribute_connect)

    def retranslateUi(self, pygisedtrend_attribute_connect):
        pygisedtrend_attribute_connect.setWindowTitle(_translate("pygisedtrend_attribute_connect", "Dialog", None))
        self.labelGstaAttribute.setText(_translate("pygisedtrend_attribute_connect", "GSTA attributes", None))
        self.comboGstaAttributeList.setItemText(0, _translate("pygisedtrend_attribute_connect", "Mean", None))
        self.comboGstaAttributeList.setItemText(1, _translate("pygisedtrend_attribute_connect", "Sorting", None))
        self.comboGstaAttributeList.setItemText(2, _translate("pygisedtrend_attribute_connect", "Skewness", None))
        self.labelShapeAttribute.setText(_translate("pygisedtrend_attribute_connect", "Shapefile attributes", None))
        self.pushButtonClearList.setText(_translate("pygisedtrend_attribute_connect", "Clear list", None))

import resources_rc
