from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis

from wikimapia_config import WikimapiaConfig
from wikimapia_settings import WikimapiaSettings
from wikimapia_widget import WikimapiaWidget

class WikimapiaApp(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, plugin_dir):
        # init properties
        self._api = None
        # init config
        self.config = WikimapiaConfig(plugin_dir)
        self.iface = qgis.utils.iface

        super(QObject, self).__init__(self.iface.mainWindow())

        self.title = self.tr('&Wikimapia')
        self.layers = []
        self.memory_layer = None
        self.memory_layer_index = 1
        # init GUI controls
        self.settings = WikimapiaSettings(self)
        self.widget = WikimapiaWidget(self)

    def api(self):
        from wikimapia_api import WikimapiaApi
        if not isinstance(self._api, WikimapiaApi):
            self._api = WikimapiaApi(self.config)
        return self._api

    def run(self):
        # Create action that will start plugin widget
        self.widget_action = QAction(
            QIcon(":/plugins/wikimapia/icons/icon.png"),
            self.tr('&Widget'),
            self.iface.mainWindow())
        self.settings_action = QAction(
            QIcon(":/plugins/wikimapia/icons/wikimapia-settings.png"),
            self.tr('&Settings'),
            self.iface.mainWindow())

        # connect the action to the run method
        self.widget_action.triggered.connect(self.runWidget)
        self.settings_action.triggered.connect(self.runSettings)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.widget_action)
        self.iface.addPluginToMenu(self.title, self.widget_action)
        self.iface.addPluginToMenu(self.title, self.settings_action)

        self.started.emit()

    def runWidget(self):
        if not self.config.complete:
            if not self.runSettings(): return
        # show widget
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.widget)

    def runSettings(self):
        self.settings.show()
        return self.settings.exec_()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removeToolBarIcon(self.widget_action)
        self.iface.removePluginMenu(self.title, self.widget_action)
        self.iface.removePluginMenu(self.title, self.settings_action)
        if self.widget: self.iface.removeDockWidget(self.widget)
        if self.memory_layer is not None and self.memory_layer.isValid():
            self.layers.append(self.memory_layer.id())
        QgsMapLayerRegistry.instance().removeMapLayers(self.layers)
        self.finished.emit()

    def retrieveLayer(self, temporary = False):
        layer = None
        if temporary is False: layer = self.memory_layer
        if layer is not None: return layer
        uri = ('Polygon?crs=epsg:4326&'
               'filed=id:integer&'
               'field=wm_id:integer&'
               'field=name:string(100)&'
               'field=description:string(5000)')
        name = 'temporary_wikimapia'
        if temporary is True:
            name += '_{:03d}'.format(self.memory_layer_index)
            self.memory_layer_index += 1
        layer = QgsVectorLayer(uri, name, 'memory')
        if not layer.isValid():
            self.iface.messageBar().pushMessage(
                'Error',
                'Error creating wikimapia layer',
                level = QgsMessageBar.CRITICAL,
                duration = 3)

        for symbol in layer.rendererV2().symbols(): symbol.setAlpha(0.5)
        QgsMapLayerRegistry.instance().addMapLayer(layer)

        if temporary is True:
            self.layers.append(layer.id())
        else:
            self.memory_layer = layer
        return layer
