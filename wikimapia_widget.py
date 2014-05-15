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
from PyQt4.QtCore import QVariant
from ui_wikimapia_widget import Ui_WikimapiaWidget

from qgis.core import *
from qgis.gui import *
import qgis

import anydbm
import os.path

import pprint

class WikimapiaWidget(QtGui.QDockWidget, Ui_WikimapiaWidget):
    def __init__(self, config):
        QtGui.QWidget.__init__(self)
        self.config = config
        self.setupUi(self)
        # a reference to our map canvas
        self.iface = qgis.utils.iface
        self.canvas = self.iface.mapCanvas() #CHANGE
        self.pointEmitter = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.boundsButton.toggled.connect(self.activateTool)
        self.categoriesEdit.editingFinished.connect(self.categoriesChanged)
        self.importButton.clicked.connect(self.doImport)
        self.tabs.currentChanged.connect(self.updateImportButton)
        self.idEdit.valueChanged.connect(self.idChanged)
        self.wgs = crs = QgsCoordinateReferenceSystem(4326)
        self.memory_layer = None
        self.memory_layer_index = 0
        self.bounds = None

    def activateTool(self, state):
        # self.iface.messageBar().pushMessage('info', str(state))
        if state:
            self.pointEmitter.canvasClicked.connect(self.selectFeature)
            self.canvas.setMapTool(self.pointEmitter)
        else:
            self.pointEmitter.canvasClicked.disconnect(self.selectFeature)
            self.canvas.unsetMapTool(self.pointEmitter)

    def categoriesChanged(self):
        self.updateImportButton()

    def idChanged(self):
        self.updateImportButton()

    def selectFeature(self, point, button):
        #self.iface.messageBar().pushMessage('info', str(point))
        layer = self.iface.activeLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushMessage(
                'Error',
                'You should use `selectTool` only with active vector layer',
                level = QgsMessageBar.WARNING,
                duration = 3)
            return
        width = self.canvas.mapUnitsPerPixel() * 2
        rect = QgsRectangle(point.x() - width,
                            point.y() - width,
                            point.x() + width,
                            point.y() + width)

        rect = self.canvas.mapRenderer().mapToLayerCoordinates(layer, rect)

        layer.select(rect, False)
        selected = layer.selectedFeatures()
        if selected:
            self.bounds = selected[0]
            layer.removeSelection()
            layer.select(self.bounds.id())
            self.boundsButton.toggle()
            self.boundsEdit.setText(str(self.bounds.id()))
            self.boundsLayer = layer
            self.updateImportButton()

    def updateImportButton(self):
        enabled = False
        current = self.tabs.currentWidget()
        if current == self.idTab:
            enabled = self.idEdit.value() > 0
        elif current == self.areaTab:
            enabled = self.bounds is not None and \
                      self.categoriesEdit.text() != ''
        self.importButton.setEnabled(enabled)

    def loadCategoryCombo(self):
        #if self.categoryCombo.count() > 0: return
        db = anydbm.open(os.path.join(self.config.db_dir, 'categories.db'), 'c')
        for id, val in db.iteritems():
            self.categoryCombo.addItem(val.decode('utf-8') + ' (id: ' + id + ')', id)
        db.close()

    def createLayer(self):
        selectedIndex = self.destCombo.currentIndex()
        if selectedIndex == 2:
            layer = self.iface.activeLayer()
            if not layer or layer.type() != QgsMapLayer.VectorLayer:
                self.iface.messageBar().pushMessage(
                    'Error',
                    'You select `current layer` as import destination but '
                    'where are no vector layer selected. Please, select '
                    'vector layer',
                    level = QgsMessageBar.FATAL,
                    duration = 3)
                return None
            return layer
        layer = None
        if selectedIndex == 0: layer = self.memory_layer
        if layer is not None: return layer
        uri = ('Polygon?crs=epsg:4326&'
               'filed=id:integer&'
               'field=wm_id:integer&'
               'field=name:string(100)&'
               'field=description:string(5000)')
        name = 'temporary_wikimapia'
        if selectedIndex == 1:
            name += '_{:03d}'.format(self.memory_layer_index)
            self.memory_layer_index += 1
        layer = QgsVectorLayer(uri, name, 'memory')
        if not layer.isValid():
            self.iface.messageBar().pushMessage(
                'Error',
                'Error creating wikimapia layer',
                level = QgsMessageBar.CRITICAL,
                duration = 3)
        if selectedIndex == 0: self.memory_layer = layer
        return layer

    def doImport(self):
        current = self.tabs.currentWidget()
        if current == self.idTab:
            self.doIdImport()
        elif current == self.areaTab:
            self.doAreaImport()

    def createPlaces(self, places, bounds = None):
        # create layer
        vl = self.createLayer()
        if vl is None: return
        prov = vl.dataProvider()
        # add a features
        for place in places:
            if 'polygon' not in place: continue
            ring = []
            for p in place['polygon']:
                ring.append(QgsPoint(p['x'], p['y']))
            geometry = QgsGeometry.fromPolygon([ring])
            if bounds and not bounds.contains(geometry): continue
            feature = QgsFeature()
            feature.setGeometry(geometry)
            title = (place['title'] if 'title' in place else '')
            descr = (place['description'] if 'description' in place else '')
            feature.setAttributes([place['id'], title, descr])
            prov.addFeatures([feature])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl.updateExtents()
        for symbol in vl.rendererV2().symbols(): symbol.setAlpha(0.5)
        QgsMapLayerRegistry.instance().addMapLayer(vl)

    def doIdImport(self):
        place = self.config.api.get_place_by_id(self.idEdit.value())
        self.createPlaces([place])
        self.iface.messageBar().pushMessage(
            'import successfull',
            'One feature imported successfully',
            duration = 3)

    def doAreaImport(self):
        t = QgsCoordinateTransform(self.boundsLayer.crs(), self.wgs)
        bounds = self.bounds.geometry()
        rect = bounds.boundingBox()
        p1 = t.transform(QgsPoint(rect.xMinimum(), rect.yMinimum()))
        p2 = t.transform(QgsPoint(rect.xMaximum(), rect.yMaximum()))
        places = self.config.api.get_place_by_area(
            p1.x(), p1.y(), p2.x(), p2.y(),
            {'category': self.categoriesEdit.text()})
        self.createPlaces(places, bounds)
        self.iface.messageBar().pushMessage(
            'import successfull',
            '{0} features imported successfully'.format(prov.featureCount()),
            duration = 3)
        self.boundsLayer.removeSelection()

'''
API response sample

{
    'availableLanguages': {
        'en': {
            'lang_id': 0,
            'lang_name': u'English',
            'native_name': u'English',
            'object_local_slug': u'Principal-Park',
            'object_url': u'http://wikimapia.org/1432/Principal-Park'
        },
        'ja': {
            'lang_id': 7,
            'lang_name': u'Japanese',
            'native_name': u'\u65e5\u672c\u8a9e',
            'object_local_slug': u'%E3%83%97%E3%83%AA%E3%83%B3%E3%82%B7%E3%83%91%E3%83%AB%E3%83%91%E3%83%BC%E3%82%AF',
            'object_url': u'http://wikimapia.org/1432/ja/%E3%83%97%E3%83%AA%E3%83%B3%E3%82%B7%E3%83%91%E3%83%AB%E3%83%91%E3%83%BC%E3%82%AF'
        }
    },
    'comments': [
        {
            'bad': 0,
            'block': False,
            'date': 1181868040,
            'good': 3,
            'is_deleted': False,
            'lang_id': 0,
            'message': u'Even though I\'m Canadian, I have visited the USA before; I\'ve been to a Cubs game once I was in Des Moines. When I was there, it was known as "Sec Taylor Stadium". No wonder how it got renamed! I\'ve been to Colorado, Iowa, Washington, Missouri, Minnesota, and a few more.',
            'moder_name': u'',
            'moder_uid': 0,
            'name': u'SchfiftyThree',
            'num': 1,
            'place_id': 1432,
            'replies': [],
            'user_id': 0,
            'user_ip': 215529526,
            'user_photo': u''
        },
        {
            'bad': 1,
            'block': False,
            'date': 1187337836,
            'good': 2,
            'is_deleted': False,
            'lang_id': 0,
            'message': u'I live less than a half-mile from the stadium. Great fireworks every Friday night!\r\n\r\nPrincipal Financial Group owns most of the office space in downtown Des Moines, which is adjacent to the stadium (Des Moines is the Insurance/Financial capitol of the world, ya know!). They purchased the stadium name a few years back to increase their already household name in central Iowa. I had a hard time swallowing this, as it was announced around the same time that the new state-of-the-art downtown entertainment arena was to be called the "Wells Fargo Arena".\r\n\r\nI fear we have precious few years before the world-famous Iowa State Fairgrounds is renamed Geiko or ING fairgrounds. I am a die-hard capitalist, but I believe commercialism should be kept on a leash by property owners and city officials.',
            'moder_name': u'',
            'moder_uid': 0,
            'name': u'DSMeTailer',
            'num': 2,
            'place_id': 1432,
            'replies': [],
            'user_id': 0,
            'user_ip': 1193715305, u'user_photo': u''
        },
        {u'bad': 0, u'block': False, u'date': 1190137086, u'good': 1, u'is_deleted': False, u'lang_id': 0, u'message': u"I don't go there very often but i have a lot of fun when i go there. the food's great, there's nuts, pretzals, nachos and a lot more to eat. not much to drink exept for icee and water.", u'moder_name': u'', u'moder_uid': 0, u'name': u'i live in iowa', u'num': 3, u'place_id': 1432, u'replies': [], u'user_id': 0, u'user_ip': 215524658, u'user_photo': u''},
        {u'bad': 0, u'block': False, u'date': 1214087358, u'good': 1, u'is_deleted': False, u'lang_id': 0, u'message': u'Has been home of Iowa state high school baseball tournament since 2005. There was an earlier Sec Taylor Stadium here that was replaced in 1992. Very nice stadium with great views of DM, but unfortunately has flooded a few times. They have continually upgraded the stadium. \r\n\r\nMany of the Chicago Cub players have done injury rehab stints here.', u'moder_name': u'', u'moder_uid': 0, u'name': u'a', u'num': 4, u'place_id': 1432, u'replies': [], u'user_id': 0, u'user_ip': -799920112, u'user_photo': u''}
    ],
    'contributedUsers': [
        {u'id': u'636615', u'name': u'bwog'},
        {u'id': 102, u'name': u'wtest_l2'},
        {u'id': 103, u'name': u'wtest_l3'},
        {u'id': 104, u'name': u'wtest_l4'}
    ],
    'deleted_photos': [],
    'description': u"Principal Park, formerly Sec Taylor Stadium, is a minor league baseball stadium located in Des Moines, Iowa. It is the home field of the Pacific Coast League's Iowa Cubs.",
    'edit_info': {
        'date': 1275671873,
        'deletion_state': False,
        'is_in_deletion_queue': False,
        'is_in_undeletion_queue': False,
        'is_unbindable': None,
        'user_id': 636615,
        'user_name': u'bwog'
    },
    'id': 1432,
    'is_building': False,
    'is_deleted': False,
    'is_protected': False,
    'is_region': False,
    'language_id': 0,
    'language_iso': u'en',
    'language_name':
    'English',
    'location': {
        'city': u'Des Moines, Iowa',
        'city_id': u'8333350',
        'cityguideDomain': u'des-moines',
        'country': u'USA',
        'country_adm_id': 232749,
        'east': -93.6150062,
        'gadm': [
            {
                'country': u'0',
                'id': u'1000',
                'is_last_level': u'0',
                'iso': None,
                'level': u'0',
                'name': u'World',
                'translation': u'World',
                'type': None
            }, {
                'country': u'233',
                'id': u'233',
                'is_last_level': u'0',
                'iso': None,
                'level': u'0',
                'name': u'United States',
                'translation': u'United States',
                'type': None
            }, {
                'country': u'233',
                'id': u'231518',
                'is_last_level': u'0',
                'iso': None, u'level': u'1', u'name': u'Iowa', u'translation': u'Iowa', u'type': None}
        ],
        'housenumber': u'1',
        'lat': 41.580174,
        'lon': -93.615953,
        'north': 41.5810147,
        'place': u'Des Moines',
        'south': 41.5793333,
        'state': u'Iowa',
        'street': u'Line Dr',
        'street_id': u'15506355',
        'west': -93.6168998,
        'zoom': 17
    },
    'nearestCities': {
        '15110047': {u'distance': 18, u'id': u'15110047', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5933645, u'lon': -93.828392, u'title': u'West Des Moines, Iowa', u'url': u'http://wikimapia.org/15110047/West-Des-Moines-Iowa'},
        '15156207': {u'distance': 120, u'id': u'15156207', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.5582646, u'lon': -94.2269897, u'title': u'Fort Dodge, Iowa', u'url': u'http://wikimapia.org/15156207/Fort-Dodge-Iowa'},
        '15947036': {u'distance': 57, u'id': u'15947036', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.4300823, u'lon': -92.9623604, u'title': u'Pella, Iowa', u'url': u'http://wikimapia.org/15947036/Pella-Iowa'},
        '1745239': {u'distance': 122, u'id': u'1745239', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.4175645, u'lon': -95.0629807, u'title': u'Atlantic, IA', u'url': u'http://wikimapia.org/1745239/Atlantic-IA'},
        '23529366': {u'distance': 23, u'id': u'23529366', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.7840788, u'lon': -93.6727917, u'title': u'Ankeny, Iowa', u'url': u'http://wikimapia.org/23529366/Ankeny-Iowa'},
        '3694791': {u'distance': 62, u'id': u'3694791', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.0865666, u'lon': -93.9372253, u'title': u'Boone, Iowa', u'url': u'http://wikimapia.org/3694791/Boone-Iowa'},
        '3968534': {u'distance': 76, u'id': u'3968534', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.0630578, u'lon': -92.9711151, u'title': u'Marshalltown, IA', u'url': u'http://wikimapia.org/3968534/Marshalltown-IA'},
        '3977064': {u'distance': 47, u'id': u'3977064', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.7206251, u'lon': -93.0845404, u'title': u'Newton, IA', u'url': u'http://wikimapia.org/3977064/Newton-IA'},
        '4687021': {u'distance': 56, u'id': u'4687021', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.0760956, u'lon': -93.6987354, u'title': u'Ames, Iowa', u'url': u'http://wikimapia.org/4687021/Ames-Iowa'},
        '8333350': {u'distance': 11, u'id': u'8333350', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.6514949, u'lon': -93.7042809, u'title': u'Des Moines, Iowa', u'url': u'http://wikimapia.org/8333350/Des-Moines-Iowa'}
    },
    'nearestComments': [
        {u'bad': u'0', u'date': u'1398480671', u'good': u'0', u'message': u'Dude, I don\'t know who you are, but I know this. You\'re the only guy who actually knows what this post was about. \r\nI knew Mr. Rehard, and I know he was "firm", but I also worked there briefly, and I know that he was a very caring person, and would not tolerate anything less than ULTIMATE customer service.\r\nThank you for understanding the original posting.\r\nBest Wishes', u'name': u'M. Dawson', u'num': u'2', u'place_id': u'9383911', u'title': u"Rehard's Conoco", u'url': u'/9383911/Rehard-s-Conoco', u'user_id': u'0'},
        {u'bad': u'0', u'date': u'1391926134', u'good': u'0', u'message': u'Verified that this was indeed land owned by Titan Tires... ran into the security guard there at station near entrance at the W side. Lots of homeless camps S in the woods.', u'name': u'Noah K', u'num': u'1', u'place_id': u'28675784', u'title': u'Former Titan Tire Plant', u'url': u'/28675784/Former-Titan-Tire-Plant', u'user_id': u'0'}, {u'bad': u'0', u'date': u'1335818629', u'good': u'1', u'message': u'Normally, I love this restaurants food. Have been a customer for years. Saturday night (28th, April 2012) went in with friends to get dinner and ended up finding 3 live cockroaches and 1 dead one in and around the counter. One of my friends got one with a napkin to make sure the lady behind the counter knew. Her attitude is that she is either very used to finding cockroaches or just did not care. After we found the 3rd cockroach, the only reply we got was "Do you still want your food?" This is beyond appalling. She could have at least cared, or faked that she did over this. I will NEVER be returning again.', u'name': u'Caligula', u'num': u'3', u'place_id': u'1493748', u'title': u'Tacos Andreas', u'url': u'/1493748/Tacos-Andreas', u'user_id': u'0'},
        {u'bad': u'0', u'date': u'1310603193', u'good': u'0', u'message': u'Creepy indeed! So cool though. :-)', u'name': u'Martin67', u'num': u'2', u'place_id': u'129597', u'title': u'Public Library of Des Moines - Central Library', u'url': u'/129597/Public-Library-of-Des-Moines-Central-Library', u'user_id': u'16768'}, {u'bad': u'0', u'date': u'1308029407', u'good': u'0', u'message': u"Sherman Hill was considered the gay area, but that's not what I've noticed. It's more a mix of everything. It also has its share of halfway houses, rehab houses, etc. in addition to a few ecletic shops (New Age, etc.) and one or two upscale restaurants located in Victorian homes. A lot of houses are old and huge and are being rehabbed. Other houses are run down. ", u'name': u'SixFive175', u'num': u'2', u'place_id': u'3305074', u'title': u'Sherman Hill Neighborhood', u'url': u'/3305074/Sherman-Hill-Neighborhood', u'user_id': u'1242440'}, {u'bad': u'0', u'date': u'1308026803', u'good': u'0', u'message': u'Principal Financial Group complex campus. This is the largest employer in Des Moines. People call this place a "Club Med" because it is one of the best places to work for. In addition, they seem to hire young people giving the campus a "beautiful people" atmosphere. The perks with working here are many: cafeterias, gyms, yoga, etc.', u'name': u'SixFive175', u'num': u'1', u'place_id': u'20213775', u'title': u'Principal Financial Group complex campus', u'url': u'/20213775/Principal-Financial-Group-complex-campus', u'user_id': u'0'},
        {u'bad': u'0', u'date': u'1267357183', u'good': u'0', u'message': u'Des Moines is a Hometown of Slipknot!!!', u'name': u'MurderMaggot', u'num': u'4', u'place_id': u'6170838', u'title': u'Downtown Des Moines', u'url': u'/6170838/Downtown-Des-Moines', u'user_id': u'0'}, {u'bad': u'0', u'date': u'1226941204', u'good': u'0', u'message': u'I thought the shoter was a former empolyee???', u'name': u'not given', u'num': u'3', u'place_id': u'7217', u'title': u'Drake Diner', u'url': u'/7217/Drake-Diner', u'user_id': u'0'}, {u'bad': u'0', u'date': u'1226771918', u'good': u'0', u'message': u'This is totally not in Windsor Heights. The elementary school of Bill Bryson and Jackie Joyner Kercy, among others. ', u'name': u'waller', u'num': u'1', u'place_id': u'8707235', u'title': u'Greenwood Elementary School', u'url': u'/8707235/Greenwood-Elementary-School', u'user_id': u'0'}, {u'bad': u'0', u'date': u'1226766645', u'good': u'0', u'message': u'Theodore Roosevelt High School. \nNickname: Roughriders\nFeeder schools: Callanan, Merril', u'name': u'Tom', u'num': u'1', u'place_id': u'220271', u'title': u'Roosevelt High School', u'url': u'/220271/Roosevelt-High-School', u'user_id': u'0'}
    ],
    'nearestHotels': {
        '188465': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 592, u'lat': 46.784542, u'lon': -92.093677, u'minrate': u'109', u'name': u'Hampton Inn Duluth-Canal Park', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/198/1984637.jpg', u'title': u' Hampton Inn Duluth-Canal Park (from 99 USD)***', u'url': u'http://www.booking.com/hotel/us/hampton-inn-duluth-canal-park.html?aid=320572&lang=en'},
        '23157': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 209, u'lat': 41.251008, u'lon': -96.081648, u'minrate': u'89', u'name': u'Regency Lodge', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/125/1257325.jpg', u'title': u' Regency Lodge (from 89 USD)***', u'url': u'http://www.booking.com/hotel/us/regency-lodge.html?aid=320572&lang=en'},
        '269147': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 754, u'lat': 47.891785, u'lon': -97.077183, u'minrate': u'109', u'name': u'Fairfield Inn Grand Forks', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/119/11974831.jpg', u'title': u' Fairfield Inn Grand Forks (from 89 USD)***', u'url': u'http://www.booking.com/hotel/us/fairfield-inn-grand-forks.html?aid=320572&lang=en'},
        '301527': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 174, u'lat': 41.658911, u'lon': -91.532349, u'minrate': u'129', u'name': u'hotelVetro', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/886/8869903.jpg', u'title': u' hotelVetro (from 129 USD)***', u'url': u'http://www.booking.com/hotel/us/vetro.html?aid=320572&lang=en'},
        '318089': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 397, u'lat': 45.13836, u'lon': -93.2713149, u'minrate': u'99', u'name': u'Country Inn & Suites Coon Rapids', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/115/11535384.jpg', u'title': u' Country Inn & Suites Coon Rapids (from 99 USD)***', u'url': u'http://www.booking.com/hotel/us/coon-rapids-plaza.html?aid=320572&lang=en'},
        '336815': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 253, u'lat': 42.4995823, u'lon': -96.4187195, u'minrate': u'69.99', u'name': u'The Sioux City Hotel & Conference Center', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/911/9110326.jpg', u'title': u' The Sioux City Hotel & Conference Center (from 54 USD)***', u'url': u'http://www.booking.com/hotel/us/sioux-city-707-4th-street-the-sioux-city.html?aid=320572&lang=en'},
        '338761': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 365, u'lat': 44.8619199, u'lon': -93.537153, u'minrate': u'102', u'name': u'Country Inn & Suites By Carlson Chanhassen', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/138/13858522.jpg', u'title': u' Country Inn & Suites By Carlson Chanhassen (from 102 USD)***', u'url': u'http://www.booking.com/hotel/us/chanhassen-591-west-78th-street.html?aid=320572&lang=en'},
        '403679': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 170, u'lat': 42.4517029, u'lon': -91.9216518, u'minrate': u'', u'name': u'Best Western Plus Independece Inn & Suites', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/946/9460060.jpg', u'title': u' Best Western Plus Independece Inn & Suites (from 99 USD)***', u'url': u'http://www.booking.com/hotel/us/bestwesternplusindependence.html?aid=320572&lang=en'},
        '430178': {u'class': u'2.0', u'currencycode': u'USD', u'distance': 338, u'lat': 43.5213051, u'lon': -96.7787539, u'minrate': u'81', u'name': u'Candlewood Suites Sioux Falls', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/146/14633930.jpg', u'title': u' Candlewood Suites Sioux Falls (from 81 USD)**', u'url': u'http://www.booking.com/hotel/us/suites-sioux-falls.html?aid=320572&lang=en'},
        '44633': {u'class': u'3.0', u'currencycode': u'USD', u'distance': 218, u'lat': 41.261228, u'lon': -96.193146, u'minrate': u'101.15', u'name': u'Hilton Garden Inn Omaha West', u'photo_url': u'http://aff.bstatic.com/images/hotel/max500/838/8386213.jpg', u'title': u' Hilton Garden Inn Omaha West (from 109 USD)***', u'url': u'http://www.booking.com/hotel/us/hilton-garden-inn-omaha-west.html?aid=320572&lang=en'}
    },
    'nearestPlaces': {
        '1139': {u'distance': 4.2, u'id': u'1139', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.6040544, u'lon': -93.654662, u'title': u'Drake University', u'url': u'http://wikimapia.org/1139/Drake-University'},
        '1509271': {u'distance': 4.7, u'id': u'1509271', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.6204453, u'lon': -93.6008522, u'title': u'Grand View College', u'url': u'http://wikimapia.org/1509271/Grand-View-College'},
        '1974726': {u'distance': 6.4, u'id': u'1974726', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.6204467, u'lon': -93.670764, u'title': u'Beaverdale Neighborhood', u'url': u'http://wikimapia.org/1974726/Beaverdale-Neighborhood'},
        '3305074': {u'distance': 2.4, u'id': u'3305074', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5918559, u'lon': -93.6408305, u'title': u'Sherman Hill Neighborhood', u'url': u'http://wikimapia.org/3305074/Sherman-Hill-Neighborhood'},
        '463822': {u'distance': 3, u'id': u'463822', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.572178, u'lon': -93.6503477, u'title': u'Iowa Arboretum', u'url': u'http://wikimapia.org/463822/Iowa-Arboretum'},
        '5229011': {u'distance': 1.3, u'id': u'5229011', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5903955, u'lon': -93.6073995, u'title': u'East Village', u'url': u'http://wikimapia.org/5229011/East-Village'},
        '582587': {u'distance': 6.3, u'id': u'582587', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5963737, u'lon': -93.6889924, u'title': u'Waveland Golf Course', u'url': u'http://wikimapia.org/582587/Waveland-Golf-Course'},
        '582636': {u'distance': 6.7, u'id': u'582636', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.605389, u'lon': -93.6883807, u'title': u'Glendale Cemetery', u'url': u'http://wikimapia.org/582636/Glendale-Cemetery'},
        '6170838': {u'distance': 1.1, u'id': u'6170838', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5839268, u'lon': -93.6287069, u'title': u'Downtown Des Moines', u'url': u'http://wikimapia.org/6170838/Downtown-Des-Moines'},
        '675417': {u'distance': 5.5, u'id': u'675417', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5652939, u'lon': -93.6785943, u'title': u'Waterworks park', u'url': u'http://wikimapia.org/675417/Waterworks-park'}
    },
    'object_type': 1,
    'parent_id': u'0',
    'photos': [],
    'polygon': [
        {u'x': -93.6168998, u'y': 41.580164},
        {u'x': -93.6168838, u'y': 41.579542},
        {u'x': -93.6166638, u'y': 41.57955},
        {u'x': -93.6165565, u'y': 41.5794858},
        {u'x': -93.6164117, u'y': 41.5794457},
        {u'x': -93.6163849, u'y': 41.5793333},
        {u'x': -93.6156499, u'y': 41.5795019},
        {u'x': -93.6156768, u'y': 41.5796182},
        {u'x': -93.6150867, u'y': 41.5797467},
        {u'x': -93.6151564, u'y': 41.5799152},
        {u'x': -93.6150974, u'y': 41.5799312},
        {u'x': -93.6150062, u'y': 41.5800556},
        {u'x': -93.6152101, u'y': 41.5806375},
        {u'x': -93.6155587, u'y': 41.5808421},
        {u'x': -93.615666, u'y': 41.5808582},
        {u'x': -93.6156929, u'y': 41.5810147},
        {u'x': -93.6165673, u'y': 41.5809424},
        {u'x': -93.6167765, u'y': 41.5806014},
        {u'x': -93.6167657, u'y': 41.5801921}
    ],
    'similarPlaces': {
        '13467743': {u'distance': 223, u'id': u'13467743', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.3279386, u'lon': -96.2729359, u'title': u'Mount Michael Benedictine Abbey', u'url': u'http://wikimapia.org/13467743/Mount-Michael-Benedictine-Abbey'},
        '17167901': {u'distance': 338, u'id': u'17167901', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 44.6119482, u'lon': -93.7852836, u'title': u'Belle Plaine Athletic Complex', u'url': u'http://wikimapia.org/17167901/Belle-Plaine-Athletic-Complex'},
        '17168912': {u'distance': 956, u'id': u'17168912', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 49.8093684, u'lon': -97.1456623, u'title': u'New Bluebombers & Bison Stadium', u'url': u'http://wikimapia.org/17168912/New-Bluebombers-Bison-Stadium'},
        '19859963': {u'distance': 3.4, u'id': u'19859963', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.5685019, u'lon': -93.5779595, u'title': u'Cownie Sports Complex', u'url': u'http://wikimapia.org/19859963/Cownie-Sports-Complex'},
        '2189180': {u'distance': 26, u'id': u'2189180', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 41.353812, u'lon': -93.54455, u'title': u'Indianola Little League Baseball Complex', u'url': u'http://wikimapia.org/2189180/Indianola-Little-League-Baseball-Complex'},
        '2203813': {u'distance': 284, u'id': u'2203813', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 43.9452177, u'lon': -94.9191714, u'title': u'Munson Field', u'url': u'http://wikimapia.org/2203813/Munson-Field'},
        '30377073': {u'distance': 581, u'id': u'30377073', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 46.718747, u'lon': -92.3657512, u'title': u'Esko High School Athletic Fields', u'url': u'http://wikimapia.org/30377073/Esko-High-School-Athletic-Fields'},
        '329014': {u'distance': 305, u'id': u'329014', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.7924877, u'lon': -96.9290551, u'title': u'Dakota Dome', u'url': u'http://wikimapia.org/329014/Dakota-Dome'},
        '3837215': {u'distance': 956, u'id': u'3837215', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 49.8082018, u'lon': -97.1483499, u'title': u'Track field', u'url': u'http://wikimapia.org/3837215/Track-field'},
        '4812363': {u'distance': 247, u'id': u'4812363', u'language_id': 0, u'language_iso': u'en', u'language_name': u'English', u'lat': 42.4444885, u'lon': -96.3660084, u'title': u'Lewis and Clark Park', u'url': u'http://wikimapia.org/4812363/Lewis-and-Clark-Park'}
    },
    'tags': [
        {u'id': 27, u'title': u'stadium'},
        {u'id': 226, u'title': u'baseball'},
        {u'id': 39351, u'title': u'MiLB - Minor League Baseball'}
    ],
    'title': u'Principal Park',
    'urlhtml': u'Principal Park',
    'wikipedia': u'http://en.wikipedia.org/wiki/Principal_Park'
}
'''
