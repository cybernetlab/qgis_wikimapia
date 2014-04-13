# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wikimapia_widget.ui'
#
# Created: Sun Apr 13 16:09:15 2014
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
        WikimapiaWidget.resize(355, 130)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WikimapiaWidget.sizePolicy().hasHeightForWidth())
        WikimapiaWidget.setSizePolicy(sizePolicy)
        WikimapiaWidget.setMinimumSize(QtCore.QSize(350, 130))
        WikimapiaWidget.setWindowTitle(_fromUtf8(""))
        self.horizontalLayout = QtGui.QHBoxLayout(WikimapiaWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabs = QtGui.QTabWidget(WikimapiaWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setMinimumSize(QtCore.QSize(330, 115))
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
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.locationButton = QtGui.QPushButton(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.locationButton.sizePolicy().hasHeightForWidth())
        self.locationButton.setSizePolicy(sizePolicy)
        self.locationButton.setMinimumSize(QtCore.QSize(110, 0))
        self.locationButton.setObjectName(_fromUtf8("locationButton"))
        self.horizontalLayout_2.addWidget(self.locationButton)
        self.categoryCombo = QtGui.QComboBox(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.categoryCombo.sizePolicy().hasHeightForWidth())
        self.categoryCombo.setSizePolicy(sizePolicy)
        self.categoryCombo.setMinimumSize(QtCore.QSize(100, 0))
        self.categoryCombo.setEditable(True)
        self.categoryCombo.setObjectName(_fromUtf8("categoryCombo"))
        self.horizontalLayout_2.addWidget(self.categoryCombo)
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
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.layerLabel = QtGui.QLabel(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.layerLabel.sizePolicy().hasHeightForWidth())
        self.layerLabel.setSizePolicy(sizePolicy)
        self.layerLabel.setObjectName(_fromUtf8("layerLabel"))
        self.horizontalLayout_3.addWidget(self.layerLabel)
        self.layerCombo = QtGui.QComboBox(self.areaTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.layerCombo.sizePolicy().hasHeightForWidth())
        self.layerCombo.setSizePolicy(sizePolicy)
        self.layerCombo.setMinimumSize(QtCore.QSize(153, 0))
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.layerCombo.addItem(_fromUtf8(""))
        self.layerCombo.addItem(_fromUtf8(""))
        self.layerCombo.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.layerCombo)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tabs.addTab(self.areaTab, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tabs)

        self.retranslateUi(WikimapiaWidget)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(WikimapiaWidget)

    def retranslateUi(self, WikimapiaWidget):
        self.locationButton.setText(_translate("WikimapiaWidget", "Select Location", None))
        self.importButton.setText(_translate("WikimapiaWidget", "Import", None))
        self.layerLabel.setText(_translate("WikimapiaWidget", "Импортировать", None))
        self.layerCombo.setItemText(0, _translate("WikimapiaWidget", "На слой Wikimapia", None))
        self.layerCombo.setItemText(1, _translate("WikimapiaWidget", "На новый слой", None))
        self.layerCombo.setItemText(2, _translate("WikimapiaWidget", "В текущий слой", None))
        self.tabs.setTabText(self.tabs.indexOf(self.areaTab), _translate("WikimapiaWidget", "By Area", None))

import resources_rc
