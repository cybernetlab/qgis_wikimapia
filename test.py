# -*- coding: utf-8 -*-
from wikimapia_api import WikimapiaApi

api = WikimapiaApi('db/config.db')
# print api.get_place_by_id('384').keys()
#i = api.get_place_by_area(55.0, 33.0, 55.3, 33.4, {'category': 1914})
i = api.get_categories()
print len(i)
print i[99]
#for n in i: print n
