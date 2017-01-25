from .key import Key
from .value import Value


class Entity:
    def __init__(self, data=None, key=None):
        self.data = data
        self.key = key

    @classmethod
    def from_api(cls, key, properties):
        key = Key.from_api(**key)
        data = {name: Value.from_api(**value) for name, value in properties}

        self = cls(data, key=key)

        return self

    def to_api(self):
        res = {}

        if self.data:
            res['properties'] = {
                name: value.to_api() if hasattr(value, 'to_api') else value
                for name, value in self.data.items()
            }
        if self.key:
            res['key'] = self.key.to_api()

        return res

    to_api_value = to_api

class EntityResult:
    def __init__(self, entity, version=None, cursor=None):
        self.entity = entity
        self.version = version
        self.cursor = cursor

    @classmethod
    def from_api(cls, entity, version=None, cursor=None):
        return cls(
            Entity.from_api(**entity),
            version = version,
            cursor = cursor,
        )

    def to_api(self):
        res = {
            'entity': self.entity.to_api(),
        }

        if self.version:
            res['version'] = self.version
        if self.cursor:
            res['cursor'] = self.cursor

        return res
