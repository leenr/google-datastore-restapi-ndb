from ..api_objects.entity import Entity, EntityResult
from ..api_objects.value import Value

from .key import key_from_ndb_key


def entity_from_ndb_model_instance(ndb_entity, app=None):
    entity = Entity(
        {
            name: Value.from_ndb_value(value, ndb_entity._properties[name])
            for name, value in ndb_entity.to_dict().items()
        },
        key = key_from_ndb_key(ndb_entity.key, app=app)
    )

    return entity

def entity_result_from_ndb_model_instance(ndb_entity):
    return EntityResult(
        entity_from_ndb_model_instance(ndb_entity),
        version = None, # at quick look, there is no way to get txnID or something similar from ndb interface
        cursor = None, # unfortunatly, same problem with this too
    )
