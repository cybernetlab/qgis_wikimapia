# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WikimapiaWidget
                                 A QGIS plugin
 wikimapia
                             -------------------
        begin                : 2014-04-12
        copyright            : (C) 2014 by Alexey Ovchinnikov
        email                : alexiss@plandex.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_wikimapia_widget import Ui_WikimapiaWidget

from qgis.core import *
from qgis.gui import *
import qgis
import time

import anydbm
import os.path

from wikimapia_import_workers import *

class WikimapiaWidget(QDockWidget, Ui_WikimapiaWidget):
    def __init__(self, app):
        QDockWidget.__init__(self, parent = app.iface.mainWindow())
        self.app = app
        self.config = app.config
        self.iface = app.iface
        self.setupUi(self)
        self.layers = QgsMapLayerRegistry.instance()
        #self.layers.legendLayersAdded.connect(self.loadBoundsCombo)
        #self.layers.layersRemoved.connect(self.loadBoundsCombo)
        self.refreshBoundsButton.clicked.connect(self.loadBoundsCombo)
        self.boundsCombo.currentIndexChanged.connect(self.boundsChanged)
        self.categoriesEdit.editingFinished.connect(self.categoriesChanged)
        self.importButton.clicked.connect(self.doImport)
        self.tabs.currentChanged.connect(self.updateImportButton)
        self.idEdit.valueChanged.connect(self.idChanged)
        self.loadBoundsCombo()

    def boundsChanged(self):
        self.updateImportButton()

    def categoriesChanged(self):
        self.updateImportButton()

    def idChanged(self):
        self.updateImportButton()

    def updateImportButton(self):
        enabled = False
        current = self.tabs.currentWidget()
        if current == self.idTab:
            enabled = self.idEdit.value() > 0
        elif current == self.areaTab:
            enabled = self.boundsCombo.currentIndex >= 0
        self.importButton.setEnabled(enabled)

    def loadBoundsCombo(self):
        layers = self.iface.legendInterface().layers()
        self.boundsCombo.clear()
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.boundsCombo.addItem(layer.name(), layer.id())

    def createProgress(self):
        # configure the QgsMessageBar
        self.messageBar = self.iface.messageBar().createMessage(
            self.tr('Importing from Wikimapia'), )
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.messageBar.layout().addWidget(self.progressBar)
        self.iface.messageBar().pushWidget(
            self.messageBar, self.iface.messageBar().INFO)

    def createBoundsLayer(self):
        self.bounds = QgsVectorLayer('polygon?crs=epsg:4326', 'bounds', 'memory')
        QgsMapLayerRegistry.instance().addMapLayer(self.bounds)

    def hideProgress(self):
        if self.messageBar: self.iface.messageBar().popWidget(self.messageBar)

    def doImport(self):
        worker = None
        current = self.tabs.currentWidget()
        if current == self.idTab:
            worker = WikimapiaImportByIdWorker(
                self.app,
                self.createLayer(),
                self.idEdit.value())
        elif current == self.areaTab:
            index = self.boundsCombo.currentIndex()
            bounds = self.layers.mapLayer(self.boundsCombo.itemData(index))
            worker = WikimapiaImportByAreaWorker(
                self.app,
                self.createLayer(),
                bounds,
                self.categoriesEdit.text())
        if worker is None: return
        self.createProgress()
        self.percents = 0
        self.setEnabled(False)

        self.createBoundsLayer()
        #worker.finished.connect(self.importFinished)
        #worker.error.connect(self.importError)
        #worker.run(self.progressBar)
        #self.importFinished(True, )
        #self.thread = thread = QThread(QThread.currentThread()) #self.iface.mainWindow())
        #worker.moveToThread(thread)
        #worker.progress.connect(self.progressBar.setValue)
        #thread.started.connect(worker.doWork)
        # self.iface.mainWindow().processEvents()
        #thread.start()
        #QgsApplication.processEvents()
        thread = QThread(self)
        worker.moveToThread(thread)
        worker.finished.connect(self.importFinished)
        worker.error.connect(self.importError)
        worker.progress.connect(self.importProgress)
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker


    def importFinished(self, success, total):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        if success:
            self.iface.messageBar().pushMessage(
                self.tr('import successfull'),
                self.tr('{0} features imported successfully').format(total),
                duration = 3)
        #if self.boundsLayer: self.boundsLayer.removeSelection()
        self.setEnabled(True)
        self.hideProgress()

    def importError(self, e, msg):
        self.iface.messageBar().pushMessage(
            self.tr('error occured while importing'),
            msg,
            level = QgsMessageBar.CRITICAL)

    def importProgress(self, total, progress, items, geom):
        percentsNew = (progress * 100) / total
        if percentsNew != self.percents:
            self.percents = percentsNew
            self.progressBar.setValue(self.percents)
        f = QgsFeature()
        f.setGeometry(geom)
        self.bounds.dataProvider().addFeatures([f])

    def createLayer(self):
        selectedIndex = self.destCombo.currentIndex()
        if selectedIndex < 2:
            return self.app.retrieveLayer(selectedIndex == 1)
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushMessage(
                'Error',
                'You select `current layer` as import destination but '
                'where are no vector layer selected. Please, select '
                'vector layer',
                level = QgsMessageBar.CRITICAL,
                duration = 3)
            return None
        return layer
