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
        locale = QSettings().value('locale/userLocale')[0:2]
        localePath = os.path.join(self.plugin_dir,
                                  'i18n',
                                  'wikimapia_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.title = self.translator.translate('Wikimapia', '&Wikimapia')
        # Create the dialog (after translation) and keep reference
        self.config = WikimapiaConfig(self.plugin_dir)
        self.widget = WikimapiaWidget(self.config)
        self.settings = WikimapiaSettings(self.config)

    def initGui(self):
        # Create action that will start plugin widget
        self.widget_action = QAction(
            QIcon(":/plugins/wikimapia/icons/icon.png"),
            self.translator.translate('Wikimapia', '&Widget'),
            self.iface.mainWindow())
        self.settings_action = QAction(
            QIcon(":/plugins/wikimapia/icons/wikimapia-settings.png"),
            self.translator.translate('Wikimapia', '&Settings'),
            self.iface.mainWindow())

        # connect the action to the run method
        self.widget_action.triggered.connect(self.run_widget)
        self.settings_action.triggered.connect(self.run_settings)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.widget_action)
        self.iface.addPluginToMenu(self.title, self.widget_action)
        self.iface.addPluginToMenu(self.title, self.settings_action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(self.title, self.widget_action)
        self.iface.removePluginMenu(self.title, self.settings_action)
        self.iface.removeToolBarIcon(self.widget_action)

    # run method that performs all the real work
    def run_widget(self):
        if not self.config.complete:
            if not self.run_settings(): return
        # show widget
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.widget)

    def run_settings(self):
        self.settings.show()
        return self.settings.exec_()
