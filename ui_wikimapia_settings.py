# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wikimapia_settings.ui'
#
# Created: Sun Apr 13 01:19:11 2014
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

class Ui_WikimapiaSettings(object):
    def setupUi(self, WikimapiaSettings):
        WikimapiaSettings.setObjectName(_fromUtf8("WikimapiaSettings"))
        WikimapiaSettings.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(WikimapiaSettings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.apiKeyLabel = QtGui.QLabel(WikimapiaSettings)
        self.apiKeyLabel.setObjectName(_fromUtf8("apiKeyLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.apiKeyLabel)
        self.apiKeyEdit = QtGui.QLineEdit(WikimapiaSettings)
        self.apiKeyEdit.setObjectName(_fromUtf8("apiKeyEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.apiKeyEdit)
        self.apiUrlLabel = QtGui.QLabel(WikimapiaSettings)
        self.apiUrlLabel.setObjectName(_fromUtf8("apiUrlLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.apiUrlLabel)
        self.apiUrlEdit = QtGui.QLineEdit(WikimapiaSettings)
        self.apiUrlEdit.setObjectName(_fromUtf8("apiUrlEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.apiUrlEdit)
        self.apiDelayLabel = QtGui.QLabel(WikimapiaSettings)
        self.apiDelayLabel.setObjectName(_fromUtf8("apiDelayLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.apiDelayLabel)
        self.apiDelayEdit = QtGui.QSpinBox(WikimapiaSettings)
        self.apiDelayEdit.setObjectName(_fromUtf8("apiDelayEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.apiDelayEdit)
        self.categoriesUpdatedLabel = QtGui.QLabel(WikimapiaSettings)
        self.categoriesUpdatedLabel.setObjectName(_fromUtf8("categoriesUpdatedLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.categoriesUpdatedLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.categoriesLabel = QtGui.QLabel(WikimapiaSettings)
        self.categoriesLabel.setObjectName(_fromUtf8("categoriesLabel"))
        self.horizontalLayout.addWidget(self.categoriesLabel)
        self.categoriesButton = QtGui.QPushButton(WikimapiaSettings)
        self.categoriesButton.setObjectName(_fromUtf8("categoriesButton"))
        self.horizontalLayout.addWidget(self.categoriesButton)
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.progressBar = QtGui.QProgressBar(WikimapiaSettings)
        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        self.buttonBox = QtGui.QDialogButtonBox(WikimapiaSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(WikimapiaSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), WikimapiaSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), WikimapiaSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(WikimapiaSettings)

    def retranslateUi(self, WikimapiaSettings):
        WikimapiaSettings.setWindowTitle(_translate("WikimapiaSettings", "Wikimapia Plugin Settings", None))
        self.apiKeyLabel.setText(_translate("WikimapiaSettings", "api key", None))
        self.apiUrlLabel.setText(_translate("WikimapiaSettings", "api url", None))
        self.apiDelayLabel.setText(_translate("WikimapiaSettings", "api delay (msec)", None))
        self.categoriesUpdatedLabel.setText(_translate("WikimapiaSettings", "categories", None))
        self.categoriesLabel.setText(_translate("WikimapiaSettings", "updated at", None))
        self.categoriesButton.setText(_translate("WikimapiaSettings", "Update now", None))

