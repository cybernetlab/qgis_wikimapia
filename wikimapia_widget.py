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

import anydbm
import os.path

class WikimapiaWidget(QtGui.QDockWidget, Ui_WikimapiaWidget):
    def __init__(self, config):
        QtGui.QWidget.__init__(self)
        self.config = config
        self.setupUi(self)
#        self.loadCategoryCombo()

#    def show(self):
#        super(WikimapiaWidget, self).show()

#    def setTextBrowser(self, output):
#        self.txtFeedback.setText(output)

#    def clearTextBrowser(self):
#        self.txtFeedback.clear()

    def changeActive(self, state):
        if state == Qt.Checked:
            QObject.connect(
                self.clickTool,
                SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"),
                self.selectFeature)
        else:
            QObject.disconnect(
                self.clickTool,
                SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"),
                self.selectFeature)

    def selectFeature(self):
        pass


    def updateImportButton(self):
        if category

    def loadCategoryCombo(self):
        # print self.categoryCombo.count
        #if self.categoryCombo.count() > 0: return
        db = anydbm.open(os.path.join(self.config.db_dir, 'categories.db'), 'c')
        for id, val in db.iteritems():
            self.categoryCombo.addItem(val.decode('utf-8') + ' (id: ' + id + ')', id)
        db.close()
