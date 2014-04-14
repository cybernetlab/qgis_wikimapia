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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant
from ui_wikimapia_widget import Ui_WikimapiaWidget

from qgis.core import *
from qgis.gui import *
import qgis

import anydbm
import os.path

class WikimapiaWidget(QtGui.QDockWidget, Ui_WikimapiaWidget):
    def __init__(self, config):
        QtGui.QWidget.__init__(self)
        self.config = config
        self.setupUi(self)
        # a reference to our map canvas
        self.iface = qgis.utils.iface
        self.canvas = self.iface.mapCanvas() #CHANGE
        self.pointEmitter = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.boundsButton.toggled.connect(self.activateTool)
        self.categoriesEdit.editingFinished.connect(self.categoriesChanged)
        self.importButton.clicked.connect(self.doImport)
        self.wgs = crs = QgsCoordinateReferenceSystem(4326)
        self.memory_layer = None
        self.memory_layer_index = 0
        self.bounds = None


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
        self.importButton.setEnabled(self.bounds is not None and self.categoriesEdit.text() != '')

    def loadCategoryCombo(self):
        #if self.categoryCombo.count() > 0: return
        db = anydbm.open(os.path.join(self.config.db_dir, 'categories.db'), 'c')
        for id, val in db.iteritems():
            self.categoryCombo.addItem(val.decode('utf-8') + ' (id: ' + id + ')', id)
        db.close()

    def createLayer(self):
        selectedIndex = self.destCombo.currentIndex()
        if selectedIndex == 2:
            layer = self.iface.activeLayer()
            if not layer or layer.type() != QgsMapLayer.VectorLayer:
                self.iface.messageBar().pushMessage(
                    'Error',
                    'You select `current layer` as import destination but '
                    'where are no vector layer selected. Please, select '
                    'vector layer',
                    level = QgsMessageBar.FATAL,
                    duration = 3)
                return None
            return layer
        layer = None
        if selectedIndex == 0: layer = self.memory_layer
        if layer is not None: return layer
        uri = ('Polygon?crs=epsg:4326&'
               'filed=id:integer&'
               'field=wm_id:integer&'
               'field=name:string(100)&'
               'field=description:string(500)')
        name = 'temporary_wikimapia'
        if selectedIndex == 1:
            name += '_{:03i}'.format(self.memory_layer_index)
            self.memory_layer_index += 1
        layer = QgsVectorLayer(uri, name, 'memory')
        if not layer.isValid():
            self.iface.messageBar().pushMessage(
                'Error',
                'Error creating wikimapia layer',
                level = QgsMessageBar.CRITICAL,
                duration = 3)
        if selectedIndex == 0: self.memory_layer = layer
        return layer

    def doImport(self):
        t = QgsCoordinateTransform(self.boundsLayer.crs(), self.wgs)
        bounds = self.bounds.geometry()
        rect = bounds.boundingBox()
        p1 = t.transform(QgsPoint(rect.xMinimum(), rect.yMinimum()))
        p2 = t.transform(QgsPoint(rect.xMaximum(), rect.yMaximum()))
        places = self.config.api.get_place_by_area(
            p1.x(), p1.y(), p2.x(), p2.y(),
            {'category': self.categoriesEdit.text()})

        # create layer
        vl = self.createLayer()
        if vl is None: return
        prov = vl.dataProvider()

        # add a features
        for place in places:
            if 'polygon' not in place: continue
            ring = []
            for p in place['polygon']:
                ring.append(QgsPoint(p['x'], p['y']))
            geometry = QgsGeometry.fromPolygon([ring])
            if not bounds.contains(geometry): continue
            feature = QgsFeature(id = place['id'])
            feature.setGeometry(geometry)
            title = (place['title'] if 'title' in place else '')
            descr = (place['description'] if 'description' in place else '')
            feature.setAttributes([place['id'], title, descr])
            prov.addFeatures([feature])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(vl)

        self.iface.messageBar().pushMessage(
            'import successfull',
            '{:i} features imported successfully'.format(prov.featureCount()),
            duration = 3)
        self.boundsLayer.removeSelection()
