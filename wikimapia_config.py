import anydbm
import os
import qgis

from wikimapia_api import API

class WikimapiaConfig(object):
    def __init__(self, plugin_dir):
        self._db_dir = os.path.join(plugin_dir, 'db')
        if not os.path.exists(self._db_dir): os.makedirs(self._db_dir)
        self._config = os.path.join(self._db_dir, 'config.db')
        self._plugin_dir = plugin_dir
        self._iface = None
        self.load()

    def load(self):
        db = anydbm.open(self._config, 'c')
        self._api_key = db.setdefault('api_key', '')
        self._api_url = db.setdefault('api_url', 'http://api.wikimapia.org/')
        self._api_delay = int(db.setdefault('api_delay', '1'))
        self._language = db.setdefault('language', 'en')
        self._categories_updated = str(db.setdefault('categories_updated', ''))
        db.close()

    def save(self):
        db = anydbm.open(self._config, 'w')
        db['api_key'] = self.api_key
        db['api_url'] = self.api_url
        db['api_delay'] = str(self.api_delay)
        db['language'] = str(self.language)
        db['categories_updated'] = str(self.categories_updated)
        db.close()

    @property
    def complete(self):
        return self._api_key and self._categories_updated

    @property
    def db_dir(self):
        return self._db_dir

    @property
    def plugin_dir(self):
        return self._plugin_dir

    @property
    def api_key(self):
        return self._api_key
    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def api_url(self):
        if not self._api_key: self._api_url = 'http://api.wikimapia.org/'
        return self._api_url
    @api_url.setter
    def api_url(self, value):
        self._api_url = value

    @property
    def language(self):
        return self._language
    @language.setter
    def language(self, value):
        self._language = value

    @property
    def api_delay(self):
        if not self._api_delay: self._api_delay = 1
        return self._api_delay
    @api_delay.setter
    def api_delay(self, value):
        self._api_delay = int(value)

    @property
    def categories_updated(self):
        return self._categories_updated
    @categories_updated.setter
    def categories_updated(self, value):
        self._categories_updated = value

    def configure_api(self):
        API.config.key = self.api_key
        API.config.url = self.api_url
        API.config.delay = self.api_delay
        API.config.language = self.language
