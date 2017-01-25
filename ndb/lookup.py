from google.appengine.ext import ndb

from ..api_objects.query import LookupResult

from .ext.lookup import get_key_async

from .entity import entity_result_from_ndb_model_instance
from .key import key_to_ndb_key


@ndb.tasklet
def _get_by_ndb_keys_async(keys, **options):
    res = yield tuple([get_key_async(key, **options) for key in keys])
    raise ndb.Return(res)

def _get_by_ndb_keys(*args, **kwargs):
    return _get_by_ndb_keys_async(*args, **kwargs).get_result()


def lookup(keys, app, options=None):
    ndb_keys = map(key_to_ndb_key, keys)
    datastore_options = options.get_options() if options else {}

    if app:
        datastore_options['force_app'] = app

    ndb_entities = _get_by_ndb_keys(ndb_keys, **datastore_options)
    entities = map(lambda ndb_entity: entity_result_from_ndb_model_instance(ndb_entity) if ndb_entity else None, ndb_entities)

    return LookupResult(keys, entities)
