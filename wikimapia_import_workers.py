from PyQt4.QtCore import *
from qgis.core import *
import traceback

class WikimapiaWorker(QObject):
    started = pyqtSignal(int)
    finished = pyqtSignal(bool, int)
    error = pyqtSignal(Exception, basestring)
    progress = pyqtSignal(int)

    def __init__(self, app):
        QObject.__init__(self, None)
        self.app = app
        self.abort = False

    @pyqtSlot()
    def run(self):
        None

    def kill(self):
        self.abort = True

class WikimapiaImportWorker(WikimapiaWorker):
    def __init__(self, app, layer, bounds = None):
        WikimapiaWorker.__init__(self, app)
        self.layer = layer
        self.provider = layer.dataProvider()
        self.bounds = bounds
        self.processed = 0
        self.created = 0
        self.percents = 0
        self.total = 0

    def next(self):
        self.processed = self.processed + 1
        if self.total == 0: return
        percentsNew = (self.processed * 100) / self.total
        if percentsNew > self.percents:
            self.percents = percentsNew
            self.progress.emit(self.percents)
            if hasattr(self, 'progressBar') and self.progressBar:
                self.progressBar.setValue(self.percents)

    def createPlace(self, place, update = True):
        if 'polygon' not in place: return False
        ring = []
        for p in place['polygon']:
            ring.append(QgsPoint(p['x'], p['y']))
        geometry = QgsGeometry.fromPolygon([ring])
        if self.bounds:
            if not self.bounds.geometry().contains(geometry): return False
        feature = QgsFeature()
        feature.setGeometry(geometry)
        title = (place['title'] if 'title' in place else '')
        descr = (place['description'] if 'description' in place else '')
        feature.setAttributes([place['id'], title, descr])
        self.provider.addFeatures([feature])
        if update is True: self.layer.updateExtents
        return True

    def createPlaces(self, places):
        for place in places:
            if self.abort is True: break
            if self.createPlace(place, False) is True: self.created += 1
            self.next()
        self.layer.updateExtents()

class WikimapiaImportByAreaWorker(WikimapiaImportWorker):
    def __init__(self, app, layer, bounds, bounds_layer, categories):
        WikimapiaImportWorker.__init__(self, app, layer, bounds)
        self.bounds_layer = bounds_layer
        self.wgs = QgsCoordinateReferenceSystem(4326)
        self.crs = QgsCoordinateTransform(self.bounds_layer.crs(), self.wgs)
        self.categories = categories

    @pyqtSlot()
    def run(self, progressBar = None):
        self.progressBar = progressBar
        try:
            rect = self.bounds.geometry().boundingBox()
            p1 = self.crs.transform(QgsPoint(rect.xMinimum(), rect.yMinimum()))
            p2 = self.crs.transform(QgsPoint(rect.xMaximum(), rect.yMaximum()))
            places = self.app.api().get_place_by_area(
                p1.x(), p1.y(), p2.x(), p2.y(),
                { 'category': self.categories })
            self.total = places.__len__()
            self.started.emit(self.total)
            self.createPlaces(places)
        except Exception as e:
            self.finished.emit(False, self.created)
            self.error.emit(e, traceback.format_exc())
            return
        self.finished.emit(True, self.created)

class WikimapiaImportByIdWorker(WikimapiaImportWorker):
    def __init__(self, app, layer, id):
        WikimapiaImportWorker.__init__(self, app, layer)
        self.id = id

    @pyqtSlot()
    def run(self, progressBar = None):
        self.progressBar = progressBar
        self.started.emit(1)
        try:
            place = self.app.api().get_place_by_id(self.id)
            self.createPlace(place)
        except Exception as e:
            self.finished.emit(False, 0)
            self.error.emit(e, traceback.format_exc())
            return
        self.finished.emit(True, 1)


