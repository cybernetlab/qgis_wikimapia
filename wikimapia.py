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

from wikimapia_app import WikimapiaApp

class Wikimapia:
    def __init__(self, iface):
        # save reference to the QGIS interface
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

        # run application
        self.app = WikimapiaApp(self.plugin_dir)

    def initGui(self):
        self.app.run()

    def unload(self):
        self.app.unload()
