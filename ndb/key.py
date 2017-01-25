from google.appengine.ext import ndb

from ..api_objects.key import Key, KeyPathElement, Partition


def partition_from_ndb_key(ndb_key, app=None):
    partition = Partition()

    partition.app = app or ndb_key.app()
    partition.namespace = ndb_key.namespace()

    return partition

def key_from_ndb_key(ndb_key, app=None):
    return Key(
        partition = partition_from_ndb_key(ndb_key, app=app),
        path = [KeyPathElement(*pair) for pair in ndb_key.pairs()],
    )

def key_to_ndb_key(key, app=None):
    return ndb.Key(
        app = app or key.partition.app,
        namespace = key.partition.namespace,
        pairs = [path_element.pair for path_element in key.path],
    )
