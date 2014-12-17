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
        # a reference to our map canvas
        self.canvas = self.iface.mapCanvas() #CHANGE
        self.pointEmitter = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.boundsButton.toggled.connect(self.activateTool)
        self.categoriesEdit.editingFinished.connect(self.categoriesChanged)
        self.importButton.clicked.connect(self.doImport)
        self.tabs.currentChanged.connect(self.updateImportButton)
        self.idEdit.valueChanged.connect(self.idChanged)
        self.bounds = None
        self.boundsLayer = None

    def activateTool(self, state):
        # self.iface.messageBar().pushMessage('info', str(state))
        if state:
            self.pointEmitter.canvasClicked.connect(self.selectFeature)
            self.canvas.setMapTool(self.pointEmitter)
        else:
            self.pointEmitter.canvasClicked.disconnect(self.selectFeature)
            self.canvas.unsetMapTool(self.pointEmitter)

    def categoriesChanged(self):
        self.updateImportButton()

    def idChanged(self):
        self.updateImportButton()

    def selectFeature(self, point, button):
        #self.iface.messageBar().pushMessage('info', str(point))
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushMessage(
                'Error',
                'You should use `selectTool` only with active vector layer',
                level = QgsMessageBar.WARNING,
                duration = 3)
            return
        width = self.canvas.mapUnitsPerPixel() * 2
        rect = QgsRectangle(point.x() - width,
                            point.y() - width,
                            point.x() + width,
                            point.y() + width)

        rect = self.canvas.mapRenderer().mapToLayerCoordinates(layer, rect)

        layer.select(rect, False)
        selected = layer.selectedFeatures()
        if selected:
            self.bounds = selected[0]
            layer.removeSelection()
            layer.select(self.bounds.id())
            self.boundsButton.toggle()
            self.boundsEdit.setText(str(self.bounds.id()))
            self.boundsLayer = layer
            self.updateImportButton()

    def updateImportButton(self):
        enabled = False
        current = self.tabs.currentWidget()
        if current == self.idTab:
            enabled = self.idEdit.value() > 0
        elif current == self.areaTab:
            enabled = True
            #enabled = self.bounds is not None and \
            #          self.categoriesEdit.text() != ''
        self.importButton.setEnabled(enabled)

    def loadCategoryCombo(self):
        #if self.categoryCombo.count() > 0: return
        db = anydbm.open(os.path.join(self.config.db_dir, 'categories.db'), 'c')
        for id, val in db.iteritems():
            self.categoryCombo.addItem(val.decode('utf-8') + ' (id: ' + id + ')', id)
        db.close()

    def createProgress(self):
        # configure the QgsMessageBar
        self.messageBar = self.iface.messageBar().createMessage(
            self.tr('Importing from Wikimapia'), )
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.messageBar.layout().addWidget(self.progressBar)
        self.iface.messageBar().pushWidget(
            self.messageBar, self.iface.messageBar().INFO)

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
            layer = self.iface.activeLayer()
            worker = WikimapiaImportByAreaWorker(
                self.app,
                self.createLayer(),
                layer,
                #self.bounds,
                #self.boundsLayer,
                self.categoriesEdit.text())
        if worker is None: return
        self.createProgress()
        self.setEnabled(False)

        worker.finished.connect(self.importFinished)
        worker.error.connect(self.importError)
        worker.run(self.progressBar)
        #self.importFinished(True, )
        #self.thread = thread = QThread(QThread.currentThread()) #self.iface.mainWindow())
        #worker.moveToThread(thread)
        #worker.progress.connect(self.progressBar.setValue)
        #thread.started.connect(worker.doWork)
        # self.iface.mainWindow().processEvents()
        #thread.start()
        #QgsApplication.processEvents()

    def importFinished(self, success, total):
        #self.worker.deleteLater()
        #self.thread.quit()
        #self.thread.wait()
        #self.thread.deleteLater()
        if success:
            self.iface.messageBar().pushMessage(
                self.tr('import successfull'),
                self.tr('{0} features imported successfully').format(total),
                duration = 3)
        if self.boundsLayer: self.boundsLayer.removeSelection()
        self.setEnabled(True)
        self.hideProgress()

    def importError(self, e, msg):
        self.iface.messageBar().pushMessage(
            self.tr('error occured while importing'),
            msg,
            level = QgsMessageBar.CRITICAL)

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
