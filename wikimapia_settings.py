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

import anydbm
from datetime import datetime
import os.path

from wikimapia_api import API

class WikimapiaSettings(QtGui.QDialog, Ui_WikimapiaSettings):
    def __init__(self, app):
        QtGui.QDialog.__init__(self)
        self.app = app
        self.config = app.config
        self.setupUi(self)
        self.categoriesButton.clicked.connect(self.updateCategories)

    def show(self):
        self.progressBar.hide()
        if self.config.complete: self.firstStartText.hide()
        self.apiKeyEdit.setText(self.config.api_key)
        self.apiUrlEdit.setText(self.config.api_url)
        self.apiDelayEdit.setValue(self.config.api_delay)
        self.languageEdit.setText(self.config.language)
        if self.config.categories_updated:
            self.categoriesLabel.setText(
                'updated at ' + str(self.config.categories_updated))
        else:
            self.categoriesButton.setText('Load now')
            self.categoriesLabel.setText('not loaded. Push "Load now" to load')
        super(WikimapiaSettings, self).show()

    def accept(self):
        if not self.apiKeyEdit.text():
            self.apiKeyEdit.setStyleSheet(
                "QLineEdit { background-color: rgb(255, 170, 170); }")
            return
        if not self.config.categories_updated:
            self.categoriesLabel.setStyleSheet(
                "QLabel { color: rgb(255, 170, 170); }")
            return
        self.saveConfig()
        super(WikimapiaSettings, self).accept()

    def saveConfig(self):
        self.config.api_key = self.apiKeyEdit.text()
        self.config.api_url = self.apiUrlEdit.text()
        self.config.api_delay = self.apiDelayEdit.value()
        self.config.language = self.languageEdit.text()
        self.config.save()

    def updateCategories(self):
        self.progressBar.show()
        self.progressBar.setValue(0)
        db = anydbm.open(os.path.join(self.config.db_dir, 'categories.db'), 'c')
        db.clear()
        self.config.configure_api()
        categories = API.categories.all()
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
        self.config.save()
