# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wikimapia_widget.ui'
#
# Created: Sat Apr 12 23:26:01 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_WikimapiaWidget(object):
    def setupUi(self, WikimapiaWidget):
        WikimapiaWidget.setObjectName(_fromUtf8("WikimapiaWidget"))
        WikimapiaWidget.resize(227, 51)
        WikimapiaWidget.setWindowTitle(_fromUtf8(""))
        self.categoriesEdit = QtGui.QLineEdit(WikimapiaWidget)
        self.categoriesEdit.setGeometry(QtCore.QRect(10, 10, 113, 25))
        self.categoriesEdit.setObjectName(_fromUtf8("categoriesEdit"))
        self.wmButton = QtGui.QPushButton(WikimapiaWidget)
        self.wmButton.setGeometry(QtCore.QRect(130, 10, 87, 27))
        self.wmButton.setCheckable(True)
        self.wmButton.setDefault(False)
        self.wmButton.setObjectName(_fromUtf8("wmButton"))

        self.retranslateUi(WikimapiaWidget)
        QtCore.QMetaObject.connectSlotsByName(WikimapiaWidget)

    def retranslateUi(self, WikimapiaWidget):
        self.wmButton.setText(_translate("WikimapiaWidget", "wm", None))

