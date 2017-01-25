from re import match

from ..errors import MalformedObjectError


class KeyPathElement:
    def __init__(self, kind, id=None):
        self.kind = kind
        self.id = id

    @classmethod
    def from_api(cls, kind, id=None, name=None, id_may_be_omitted=False):
        if not 1 <= len(unicode(kind)) <= 1500:
            raise MalformedObjectError('A kind must not contain more than 1500 bytes when UTF-8 encoded. Cannot be "".', prop='kind')

        if (id and name) or (not id_may_be_omitted and (not id and not name)):
            raise MalformedObjectError('Key must contain exactly one of: id or name')

        return cls(kind, id or name)

    def to_api(self):
        return {
            'kind': self.kind,
            'name': unicode(self.id),
        }

    @property
    def pair(self):
        return (self.kind, self.id)

class Key:
    def __init__(self, partition, path):
        self.partition = partition
        self.path = path

    @classmethod
    def from_api(cls, path, partitionId=None, last_id_may_be_omitted=False, default_app=None):
        if partitionId is None:
            partitionId = {}

        if not 1 <= len(path) <= 100:
            raise MalformedObjectError('A path can never be empty, and a path can have at most 100 elements.', prop='path')

        return cls(
            partition = Partition.from_api(default_app=default_app, **partitionId),
            path = [
                KeyPathElement.from_api(
                    id_may_be_omitted = (last_id_may_be_omitted and i == len(path)),
                    **path_element
                ) for i, path_element in enumerate(path)
            ],
        )

    def to_api(self):
        return {
            'partition': self.partition.to_api(),
            'path': [path_element.to_api() for path_element in self.path]
        }

class Partition:
    @classmethod
    def from_api(cls, namespaceId='', projectId=None, default_app=None):
        if not cls._validate_dimension_str(namespaceId):
            raise MalformedObjectError(prop='namespaceId')
        if projectId and not cls._validate_dimension_str(projectId):
            raise MalformedObjectError(prop='projectId')

        self = cls()

        self.app = projectId or default_app
        self.namespace = namespaceId

        return self

    def to_api(self):
        res = {
            'projectId': self.app,
        }

        if self.namespace != '':
            res['namespaceId'] = self.namespace

        return res

    @staticmethod
    def _validate_dimension_str(string):
        return match('[A-Za-z\d\.\-_]{0,100}', string)
