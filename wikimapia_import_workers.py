from PyQt4.QtCore import *
from qgis.core import *
import traceback
import math

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
        if layer and layer.isValid():
            self.layer = layer
            self.provider = layer.dataProvider()
        self.bounds = bounds
        self.processed = 0
        self.created = 0
        self.percents = 0
        self.total = 0
        self.ids = []

    def next(self):
        self.processed = self.processed + 1
        if self.total == 0: return
        percentsNew = (self.processed * 100) / self.total
        if percentsNew > self.percents:
            self.percents = percentsNew
            self.progress.emit(self.percents)
            if hasattr(self, 'progressBar') and self.progressBar:
                self.progressBar.setValue(self.percents)

    def createPlace(self, place, bounds, update = True):
        if 'polygon' not in place: return False

        # check if feature with same wm_id is already in layer
        if place['id'] in self.ids: return True

        ring = [QgsPoint(p['x'], p['y']) for p in place['polygon']]
        geometry = QgsGeometry.fromPolygon([ring])
        if not bounds.contains(geometry.centroid()): return False
        self.ids.append(place['id'])
        feature = QgsFeature()
        feature.setGeometry(geometry)
        title = (place['title'] if 'title' in place else '')
        descr = (place['description'] if 'description' in place else '')
        is_building = 0
        if 'is_building' in place and place['is_building'] == True:
            is_building = 1
        is_region = 0
        if 'is_region' in place and place['is_region'] == True:
            is_region = 1
        is_deleted = 0
        if 'is_deleted' in place and place['is_deleted'] == True:
            is_deleted = 1
        categories = []
        tags = []
        if 'tags' in place:
            tags = [x['title'] for x in place['tags']]
            categories = [str(x['id']) for x in place['tags']]
        categories = ','.join(categories)
        tags = ','.join(tags)
        feature.setAttributes([place['id'], title, descr, is_building,
                               is_region, is_deleted, categories, tags])
        self.provider.addFeatures([feature])
        if update is True: self.layer.updateExtents
        return True

    def createPlaces(self, places, bounds):
        for place in places:
            if self.abort is True: break
            if self.createPlace(place, bounds, False) is True: self.created += 1
            self.next()
        self.layer.updateExtents()

class WikimapiaImportByAreaWorker(WikimapiaImportWorker):
    #MIN_HEIGHT = 12100 / 10000000
    #MAX_AREA = 14641000000 / 10000000
    MAX_AREA = 0.01
    SPLIT_SIZE = math.sqrt(MAX_AREA) * 0.8

    def __init__(self, app, layer, bounds_layer, categories):
        self.bounds_layer = bounds_layer
        self.wgs = QgsCoordinateReferenceSystem(4326)
        self.crs = QgsCoordinateTransform(bounds_layer.crs(), self.wgs)
        self.categories = categories
        # make union of all features in boundaries layer
        boundary = QgsGeometry.unaryUnion([f.geometryAndOwnership() for f in bounds_layer.getFeatures()])
        # transfrom boundaries into 4326
        boundary.transform(self.crs)
        # get bounds as a list of polygons
        if boundary.isMultipart():
            bounds = [QgsGeometry.fromPolygon(p) for p in boundary.asMultiPolygon()]
        else:
            bounds = [QgsGeometry.fromPolygon(boundary.asPolygon())]
        self.splitBoundaries(bounds)
        WikimapiaImportWorker.__init__(self, app, layer, bounds)

    def wellBoundary(self, geom):
        r = geom.boundingBox()
        #return (r.height() > self.MIN_HEIGHT and
        #        r.width() * r.height() < self.MAX_AREA)
        return r.width() * r.height() < self.MAX_AREA

    def splitGeom(self, geom, rect, dx, dy):
        x2 = rect.xMaximum() if dx == 0 else rect.xMinimum()
        y2 = rect.yMaximum() if dy == 0 else rect.yMinimum()
        p1 = QgsPoint(rect.xMinimum() + dx, rect.yMinimum() + dy)
        p2 = QgsPoint(x2 + dx, y2 + dy)
        result = []
        while p1.x() < rect.xMaximum() and p1.y() < rect.yMaximum():
            reshaped, splitted, points = geom.splitGeometry([p1, p2], True)
            if reshaped != 0: break
            result.append(geom)
            geom = splitted.pop(0)
            for g in splitted:
                result += self.splitGeom(g, g.boundingBox(), dx, dy)
            p1.set(p1.x() + dx, p1.y() + dy)
            p2.set(p2.x() + dx, p2.y() + dy)
        if geom: result.append(geom)
        return result

    def splitBoundaries(self, bounds):
        bad = [g for g in bounds if not self.wellBoundary(g)]
        while bad:
            for g in bad:
                bounds.remove(g)
                r = g.boundingBox()
                #if r.height() <= self.MIN_HEIGHT: continue
                if round(r.height(), 10) > round(self.SPLIT_SIZE, 10):
                    bounds += self.splitGeom(g, r, 0, self.SPLIT_SIZE)
                elif round(r.width(), 10) > round(self.SPLIT_SIZE, 10):
                    bounds += self.splitGeom(g, r, self.SPLIT_SIZE, 0)
            bad = [g for g in bounds if not self.wellBoundary(g)]

        #target = QgsVectorLayer('polygon?crs=epsg:4326', 'test', 'memory')
        #for geom in bounds:
        #    f = QgsFeature()
        #    f.setGeometry(geom)
        #    target.dataProvider().addFeatures([f])
        #QgsMapLayerRegistry.instance().addMapLayer(target)

    @pyqtSlot()
    def run(self, progressBar = None):
        #target = QgsVectorLayer('polygon?crs=epsg:4326', 'test', 'memory')
        #self.finished.emit(True, 0)
        #return
        self.progressBar = progressBar
        try:
            self.total = 0
            self.started.emit(self.total)
            for geom in self.bounds:
                #f = QgsFeature()
                #f.setGeometry(geom)
                #target.dataProvider().addFeatures([f])

                rect = geom.boundingBox()
                p1 = QgsPoint(rect.xMinimum(), rect.yMinimum())
                p2 = QgsPoint(rect.xMaximum(), rect.yMaximum())
                places = self.app.api().get_place_by_area(
                    p1.x(), p1.y(), p2.x(), p2.y(),
                    { 'category': self.categories })
                self.total += places.__len__()
                self.createPlaces(places, geom)

            #QgsMapLayerRegistry.instance().addMapLayer(target)
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


