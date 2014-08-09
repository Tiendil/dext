# coding: utf-8
import uuid
import contextlib
import functools

from dext.settings import settings


class BaseStorage(object):
    SETTINGS_KEY = None
    EXCEPTION = None

    def _construct_object(self, model):
        raise NotImplementedError()

    def refresh(self):
        raise NotImplementedError()

    def has_objects(self):
        raise NotImplementedError()

    def __init__(self):
        self.clear()
        self._postpone_version_update_nesting = 0
        self._update_version_requested = False

    @property
    def version(self):
        self.sync()
        return self._version

    def sync(self, force=False):
        if self.SETTINGS_KEY not in settings:
            self.update_version()
            self.refresh()
            return

        if self._version != settings[self.SETTINGS_KEY]:
            self.refresh()
            return

        if force:
            self.refresh()
            return

    def _get_next_version(self):
        return uuid.uuid4().hex

    def _setup_version(self):
        self._version = self._get_next_version()
        settings[self.SETTINGS_KEY] = str(self._version)
        self._update_version_requested = False

    def update_version(self):
        self._update_version_requested = True

        if self._postpone_version_update_nesting > 0:
            return

        self._setup_version()

    @contextlib.contextmanager
    def _postpone_version_update(self):
        self._postpone_version_update_nesting += 1

        yield

        self._postpone_version_update_nesting -= 1

        if self._update_version_requested:
            self.update_version()

    def postpone_version_update(self, func=None):

        if func is None:
            return self._postpone_version_update()

        @functools.wraps(func)
        def wrapper(*argv, **kwargs):
            with self._postpone_version_update():
                return func(*argv, **kwargs)

        return wrapper



class Storage(BaseStorage):

    def _get_all_query(self):
        raise NotImplementedError()

    def refresh(self):
        self.clear()

        self._version = settings[self.SETTINGS_KEY]

        for model in self._get_all_query():
            self.add_item(model.id, self._construct_object(model))

    def __getitem__(self, id_):
        self.sync()

        if id_ not in self._data:
            raise self.EXCEPTION(message='no object with id: %s' % id_)

        return self._data[id_]

    def add_item(self, id_, item):
        '''
        only for add new items, not for any other sort of management
        '''
        self._data[id_] = item

    def __contains__(self, id_):
        self.sync()
        return id_ in self._data

    def get(self, id_, default=None):
        self.sync()

        if id_ in self._data:
            return self._data[id_]
        return default

    def all(self):
        self.sync()

        return self._data.values()

    def clear(self):
        self._data = {}
        self._version = None
        self._update_version_requested = False

    def has_objects(self):
        return bool(self._data)

    def save_all(self):
        with self.postpone_version_update():
            for record in self._data.values():
                record.save()


class CachedStorage(Storage):

    def _reset_cache(self):
        raise NotImplementedError()

    def _update_cached_data(self, item):
        raise NotImplementedError()

    def add_item(self, id_, item):
        super(CachedStorage, self).add_item(id_, item)
        self._update_cached_data(item)

    def refresh(self):
        self._reset_cache()
        super(CachedStorage, self).refresh()

    def clear(self):
        self._reset_cache()
        super(CachedStorage, self).clear()


class SingleStorage(BaseStorage):

    @property
    def item(self):
        self.sync()
        return self._item

    def set_item(self, item):
        self._item = item
        self.update_version()

    def clear(self):
        self._item = None
        self._version = None
        self._update_version_requested = False

    def has_objects(self):
        return self._item is not None
