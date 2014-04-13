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

    def doImport(self):
        t = QgsCoordinateTransform(self.boundsLayer.crs(), self.wgs)
        rect = self.bounds.geometry().boundingBox()
        p1 = t.transform(QgsPoint(rect.xMinimum(), rect.yMinimum()))
        p2 = t.transform(QgsPoint(rect.xMaximum(), rect.yMaximum()))
        places = self.config.api.get_place_by_area(
            p1.x(), p1.y(), p2.x(), p2.y(),
            {'category': self.categoriesEdit.text()})

        # create layer
        vl = QgsVectorLayer("Wikimapia", "temporary_wikimapia", "memory")
        prov = vl.dataProvider()

        # add fields
        #pr.addAttributes( [ QgsField("name", QVariant.String),
        #                    QgsField("age",  QVariant.Int),
        #                    QgsField("size", QVariant.Double) ] )

        # add a feature
        total = 0
        for place in places:
            #if 'polygon' not in place: continue
            ring = []
            for p in place['polygon']:
                ring.append(t.transform(
                    QgsPoint(p['x'], p['y']),
                    QgsCoordinateTransform.ReverseTransform))
            feature = QgsFeature()
            geometry = QgsGeometry()
            geometry.addRing(ring)
            feature.setGeometry(geometry)
            #fet.setAttributes(["Johny", 2, 0.3])
            prov.addFeatures([feature])
            total += 1
        self.iface.messageBar().pushMessage('total', str(total))

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(vl)

