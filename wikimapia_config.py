import anydbm

class WikimapiaConfig(object):
    def __init__(self, config = 'wikimapia'):
        if not isinstance(config, basestring): config = 'wikimapia'
        db = anydbm.open(config, 'c')
        self._api_key = db.setdefault('api_key', '')
        self._api_url = db.setdefault('api_url', 'http://api.wikimapia.org/')
        self._api_delay = int(db.setdefault('api_delay', '1'))
        self._categories_updated = str(db.setdefault('categories_updated', ''))
        db.close()
        self.config = config

    @property
    def api_key(self):
        return self._api_key
    @api_key.setter
    def api_key(self, value):
        db = anydbm.open(self.config, 'w')
        self._api_key = value
        db['api_key'] = value
        db.close()
        return value

    @property
    def api_url(self):
        if not self._api_key: self._api_url = 'http://api.wikimapia.org/'
        return self._api_url
    @api_url.setter
    def api_url(self, value):
        db = anydbm.open(self.config, 'w')
        self._api_url = value
        db['api_url'] = value
        db.close()
        return value

    @property
    def api_delay(self):
        if not self._api_delay: self._api_delay = 1
        return self._api_delay
    @api_delay.setter
    def api_delay(self, value):
        db = anydbm.open(self.config, 'w')
        self._api_delay = int(value)
        db['api_delay'] = str(value)
        db.close()
        return value

    @property
    def categories_updated(self):
        return self._categories_updated
    @categories_updated.setter
    def categories_updated(self, value):
        db = anydbm.open(self.config, 'w')
        self._categories_updated = value
        db['categories_updated'] = str(value)
        db.close()
        return value

