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
from wikimapia_config import WikimapiaConfig
from wikimapia_api import WikimapiaApi

class WikimapiaWidget(QtGui.QDockWidget, Ui_WikimapiaWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.api = WikimapiaApi()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

#    def setTextBrowser(self, output):
#        self.txtFeedback.setText(output)

#    def clearTextBrowser(self):
#        self.txtFeedback.clear()
