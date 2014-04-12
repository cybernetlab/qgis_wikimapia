# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wikimapia.ui'
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

class Ui_Wikimapia(object):
    def setupUi(self, Wikimapia):
        Wikimapia.setObjectName(_fromUtf8("Wikimapia"))
        Wikimapia.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Wikimapia)
        self.buttonBox.setGeometry(QtCore.QRect(110, 251, 281, 41))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.txtFeedback = QtGui.QTextBrowser(Wikimapia)
        self.txtFeedback.setGeometry(QtCore.QRect(10, 10, 381, 241))
        self.txtFeedback.setObjectName(_fromUtf8("txtFeedback"))
        self.chkActivate = QtGui.QCheckBox(Wikimapia)
        self.chkActivate.setGeometry(QtCore.QRect(10, 260, 101, 31))
        self.chkActivate.setObjectName(_fromUtf8("chkActivate"))

        self.retranslateUi(Wikimapia)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Wikimapia.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Wikimapia.reject)
        QtCore.QMetaObject.connectSlotsByName(Wikimapia)

    def retranslateUi(self, Wikimapia):
        Wikimapia.setWindowTitle(_translate("Wikimapia", "Plandex", None))
        self.chkActivate.setText(_translate("Wikimapia", "Activate\n"
"(check)", None))

