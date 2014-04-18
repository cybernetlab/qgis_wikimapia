# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wikimapia_widget.ui'
#
# Created: Fri Apr 18 15:28:32 2014
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
        WikimapiaWidget.resize(378, 200)
        WikimapiaWidget.setMinimumSize(QtCore.QSize(0, 200))
        WikimapiaWidget.setWindowTitle(_fromUtf8(""))
        self.horizontalLayout = QtGui.QHBoxLayout(WikimapiaWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabs = QtGui.QTabWidget(WikimapiaWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setMinimumSize(QtCore.QSize(360, 180))
        self.tabs.setTabPosition(QtGui.QTabWidget.South)
        self.tabs.setObjectName(_fromUtf8("tabs"))
        self.areaTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.areaTab.sizePolicy().hasHeightForWidth())
        self.areaTab.setSizePolicy(sizePolicy)
        self.areaTab.setMinimumSize(QtCore.QSize(0, 90))
        self.areaTab.setObjectName(_fromUtf8("areaTab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.areaTab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.boundsLabel = QtGui.QLabel(self.areaTab)
        self.boundsLabel.setObjectName(_fromUtf8("boundsLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.boundsLabel)
        self.categoriesLabel = QtGui.QLabel(self.areaTab)
        self.categoriesLabel.setObjectName(_fromUtf8("categoriesLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.categoriesLabel)
        self.categoriesEdit = QtGui.QLineEdit(self.areaTab)
        self.categoriesEdit.setObjectName(_fromUtf8("categoriesEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.categoriesEdit)
        self.destLabel = QtGui.QLabel(self.areaTab)
        self.destLabel.setObjectName(_fromUtf8("destLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.destLabel)
        self.destCombo = QtGui.QComboBox(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.destCombo.sizePolicy().hasHeightForWidth())
        self.destCombo.setSizePolicy(sizePolicy)
        self.destCombo.setMinimumSize(QtCore.QSize(153, 0))
        self.destCombo.setObjectName(_fromUtf8("destCombo"))
        self.destCombo.addItem(_fromUtf8(""))
        self.destCombo.addItem(_fromUtf8(""))
        self.destCombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.destCombo)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.boundsEdit = QtGui.QLineEdit(self.areaTab)
        self.boundsEdit.setObjectName(_fromUtf8("boundsEdit"))
        self.horizontalLayout_3.addWidget(self.boundsEdit)
        self.boundsButton = QtGui.QToolButton(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boundsButton.sizePolicy().hasHeightForWidth())
        self.boundsButton.setSizePolicy(sizePolicy)
        self.boundsButton.setMinimumSize(QtCore.QSize(110, 0))
        self.boundsButton.setCheckable(True)
        self.boundsButton.setObjectName(_fromUtf8("boundsButton"))
        self.horizontalLayout_3.addWidget(self.boundsButton)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.importButton = QtGui.QPushButton(self.areaTab)
        self.importButton.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.importButton.sizePolicy().hasHeightForWidth())
        self.importButton.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/wikimapia/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.importButton.setIcon(icon)
        self.importButton.setObjectName(_fromUtf8("importButton"))
        self.horizontalLayout_2.addWidget(self.importButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tabs.addTab(self.areaTab, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tabs)

        self.retranslateUi(WikimapiaWidget)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(WikimapiaWidget)

    def retranslateUi(self, WikimapiaWidget):
        self.boundsLabel.setText(_translate("WikimapiaWidget", "boundaries", None))
        self.categoriesLabel.setText(_translate("WikimapiaWidget", "categories", None))
        self.destLabel.setText(_translate("WikimapiaWidget", "target", None))
        self.destCombo.setItemText(0, _translate("WikimapiaWidget", "Wikimapia layer", None))
        self.destCombo.setItemText(1, _translate("WikimapiaWidget", "New temporary layer", None))
        self.destCombo.setItemText(2, _translate("WikimapiaWidget", "Current layer", None))
        self.boundsButton.setText(_translate("WikimapiaWidget", "Select Location", None))
        self.importButton.setText(_translate("WikimapiaWidget", "Import", None))
        self.tabs.setTabText(self.tabs.indexOf(self.areaTab), _translate("WikimapiaWidget", "By Area", None))

import resources_rc
