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
from ui_wikimapia_settings import Ui_WikimapiaSettings
from wikimapia_config import WikimapiaConfig
from wikimapia_api import WikimapiaApi

import anydbm
from datetime import datetime

class WikimapiaSettings(QtGui.QDialog, Ui_WikimapiaSettings):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.config = WikimapiaConfig()
        self.setupUi(self)
        self.progressBar.hide()
        self.categoriesButton.clicked.connect(self.updateCategories)
        self.apiKeyEdit.setText(self.config.api_key)
        self.apiUrlEdit.setText(self.config.api_url)
        self.apiDelayEdit.setValue(self.config.api_delay)
        if self.config.categories_updated:
            self.categoriesLabel.setText(
                'updated at ' + str(self.config.categories_updated))
        else:
            self.categoriesButton.setText('Load now')
            self.categoriesLabel.setText('not loaded. Push "Load now" to load')

    def accept(self):
        super(WikimapiaSettings, self).accept()

    def saveConfig(self):
        self.config.api_key = self.apiKeyEdit.text()
        self.config.api_url = self.apiUrlEdit.text()
        self.config.api_delay = self.apiDelayEdit.value()

    def updateCategories(self):
        self.progressBar.show()
        self.progressBar.setValue(0)
        db = anydbm.open('categories', 'c')
        db.clear()
        api = WikimapiaApi()
        categories = api.get_categories()
        self.progressBar.setMaximum(len(categories))
        for cat in categories:
            db[str(cat['id'])] = cat['name'].encode('utf-8')
            self.progressBar.setValue(self.progressBar.value() + 1)
        self.config.categories_updated = datetime.today()
        db.close()
        self.progressBar.hide()
        self.categoriesButton.setText('Update now')
        self.categoriesLabel.setText(
            'updated at ' + str(self.config.categories_updated))
