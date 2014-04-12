# -*- coding: utf-8 -*-

from wikimapia_config import WikimapiaConfig

import httplib
import urllib
from urlparse import urlparse
import time
import json

class WikimapiaIterator(object):
    def __init__(self, api, function, key, opts = {}):
        if not isinstance(api, WikimapiaApi):
            raise TypeError('Wrong WikimapiaApi')
        self.total = 0
        self.loaded = -1
        self.buffer = []

        self.api = api
        self.function = function
        self.key = key
        self.opts = opts

        self.max = self.opts.pop('max', None)
        self.page_specified = 'page' in self.opts
        self.page = self.opts.setdefault('page', 1)
        self.page_size = int(self.opts.setdefault('count', '100'))

    def __iter__(self):
        return self

    def __len__(self):
        if self.max is None:
            return self.api.count_array(self.function, self.opts)
        else:
            return min(self.max, self.api.count_array(self.function, self.opts))

    def __getitem__(self, key):
        if not isinstance(key, (int, long)): raise TypeError('Wrong key')
        length = self.__len__()
        if key < 0: key = length + key
        if key < 0 or key > length:
            raise TypeError('Key out of bounds')
        if key / self.page_size == self.page - 1:
            if not self.buffer: self.__next_page()
            if not self.buffer: return None
            return self.buffer[key]
        result = self.__load_page(key / self.page_size + 1)
        if result is None: return None
        return self.buffer[key % self.page_size]

    def __load_page(self, page):
        self.opts['page'] = str(page)
        #self.opts['count'] = str(self.page_size)
        result = self.api.request(self.function, self.opts)
        if not isinstance(result, dict) or self.key not in result: return None
        return result

    def __next_page(self):
        if self.max is not None and self.loaded >= self.max: return
        self.buffer = []
        if self.loaded < self.total:
            result = self.__load_page(self.page)
            if result is None: return
            self.loaded += int(result['count'])
            if self.total == 0: self.total = int(result['found'])
            self.page += 1
            self.buffer += result[self.key]
        if self.page_specified: self.max = self.loaded

    def next(self):
        if not self.buffer: self.__next_page()
        if not self.buffer: raise StopIteration
        return self.buffer.pop(0)

class WikimapiaApi(object):
    def __init__(self, config = None):
        if isinstance(config, WikimapiaConfig):
            self.config = config
        else:
            self.config = WikimapiaConfig(config)
        self.last_call = None

    def get_place_by_id(self, id):
        return self.request('place.getbyid', {'id': id})

    def get_place_by_area(self, x1, y1, x2, y2, opts = {}):
        opts['bbox'] = "{x1},{y1},{x2},{y2}".format(**locals())
        return WikimapiaIterator(self, 'place.getbyarea', 'places', opts)

    def get_categories(self, name = None):
        opts = {}
        if isinstance(name, basestring): opts['name'] = name
        return WikimapiaIterator(self, 'category.getall', 'categories', opts)

    def get_category(self, id):
        if not isinstance(id, (int, long)) or id <= 0: return None
        result = self.request('category.getbyid', {'id': str(id)})
        if not isinstance(result, dict) or 'category' not in result:
            return None
        return result['category']

    def request(self, function, opts = {}):
        if not isinstance(self.config, WikimapiaConfig): return None
        opts['key'] = self.config.api_key
        opts['function'] = function
        opts['format'] = 'json'
        opts['language'] = 'ru'
        params = urllib.urlencode(opts)
        uri = urlparse(self.config.api_url)
        conn = httplib.HTTPConnection(uri.netloc)
        while True:
            result = None
            now = int(round(time.time() * 1000))
            if self.last_call is not None:
                if now - self.last_call < self.config.api_delay:
                    time.sleep((self.config.api_delay - self.last_call + now)
                               / 1000.0)
            try:
                conn.request('GET', uri.path + '?' + params)
                response = conn.getresponse()
            except httplib.HTTPException:
                self.last_call = int(round(time.time() * 1000))
                return None
            else:
                self.last_call = int(round(time.time() * 1000))
                if response.status != httplib.OK: return None
                result = json.loads(response.read())
                conn.close()
            if (isinstance(result, dict) and
                'debug' in result and
                result['debug']['code'] == 1004):
                time.sleep(110.0 / 1000.0)
            else:
                return result

    def count_array(self, req, opts = {}):
        opts['page'] = 1
        count = None
        if 'count' in opts: count = opts['count']
        opts['count'] = 5
        result = self.request(req, opts)
        if count is not None: opts['count'] = count
        if isinstance(result, dict) and 'found' in result:
            return int(result['found'])
        else:
            return 0

    def load_array(self, req, key, opts = {}):
        total = 0
        loaded = -1
        page_specified = False
        if 'page' in opts:
            page = int(opts['page'])
            page_specified = True
        else:
            page = 1
        max = opts.pop('max', None)
        opts.setdefault('count', '100')
        arr = []
        while loaded < total:
            opts['page'] = str(page)
            result = self.request(req, opts)
            if not isinstance(result, dict) or key not in result: return None
            loaded += int(result['count'])
            if total == 0: total = int(result['found'])
            page += 1
            arr.append(result[key])
            if page_specified or max is not None and loaded >= max: break
        return arr
