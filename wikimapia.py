# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Wikimapia
                                 A QGIS plugin
 wikimapia access
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources_rc
import os.path

from wikimapia_config import WikimapiaConfig
from wikimapia_settings import WikimapiaSettings
from wikimapia_widget import WikimapiaWidget


class Wikimapia:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir,
                                  'i18n',
                                  'wikimapia_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.config = WikimapiaConfig(self.plugin_dir, iface)

        # Create the dialog (after translation) and keep reference
        self.widget = WikimapiaWidget(self.config)
        self.settings = WikimapiaSettings(self.config)

    def initGui(self):
        # Create action that will start plugin widget
        self.action = QAction(
            QIcon(":/plugins/wikimapia/icon.png"),
            u"wikimapia", self.iface.mainWindow())
        self.settings_action = QAction(
            QIcon(":/plugins/wikimapia/icon.png"),
            u"settings", self.iface.mainWindow())

        # connect the action to the run method
        self.action.triggered.connect(self.run)
        self.settings_action.triggered.connect(self.run_settings)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&wikimapia", self.action)
        self.iface.addPluginToMenu(u"&wikimapia", self.settings_action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&wikimapia", self.action)
        self.iface.removePluginMenu(u"&wikimapia", self.settings_action)
        #self.iface.removePluginMenu(u"&plandex", self.settings_action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        if not self.config.complete():
            if not self.run_settings(): return
        # show widget
        self.addDockWidget(self.widget, Qt.LeftDockWidgetArea)

    def run_settings(self):
        self.settings.show()
        return self.settings.exec_()

    def addDockWidget(self, wdg, position = None):
        self.iface.addDockWidget(position, wdg)
