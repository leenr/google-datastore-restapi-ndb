from datetime import date, datetime, time

from google.appengine.api import users
from google.appengine.ext import db, ndb

from ..errors import MalformedObjectError


TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

class Value:
    meaning = None

    @classmethod
    def from_api(cls, excludeFromIndexes=False, meaning=None, **values):
        # lazy load to avoid circular import
        from .entity import Entity
        from .key import Key

        self = cls()

        if len(values) != 1:
            raise MalformedObjectError('value_type union can only contain exactly one property.', prop='value_type')

        api_prop_name = values.keys()[0]

        if 'nullValue' in values:
            self.value = None

        elif 'booleanValue' in values:
            self.value = bool(values['booleanValue'])
        elif 'integerValue' in values:
            self.value = int(values['integerValue'])
        elif 'doubleValue' in values:
            self.value = float(values['doubleValue'])

        elif 'timestampValue' in values:
            self.value = datetime.strptime(values['timestampValue'], TIMESTAMP_FORMAT)

        elif 'keyValue' in values:
            self.value = Key.from_api(**values['keyValue'])

        elif 'stringValue' in values:
            self.value = unicode(values['stringValue'])
        elif 'blobValue' in values:
            self.value = bytes(values['blobValue'])

        elif 'geoPointValue' in values:
            self.value = LatLng(**values['geoPointValue'])

        elif 'entityValue' in values:
            self.value = Entity.from_api(**values['entityValue'])
        elif 'arrayValue' in values:
            self.value = ArrayValue.from_api(*values['arrayValue'])

        else:
            raise MalformedObjectError('Unknown value type: {}'.format(api_prop_name), prop=api_prop_name)

        self.meaning = meaning

        self.indexed = not excludeFromIndexes
        self.api_prop_name = api_prop_name

        return self

    def to_api(self):
        res = {self.api_prop_name: self.to_api_value()}

        if not self.indexed:
            res['excludeFromIndexes'] = True
        if self.meaning is not None:
            res['meaning'] = self.meaning

        return res

    # TODO: move to rest_v1.ndb
    def to_ndb_value(self):
        return self.value.to_ndb_value() if hasattr(self.value, 'to_ndb_value') else self.value

    def to_api_value(self):
        if hasattr(self.value, 'to_api_value'):
            return self.value.to_api_value()
        elif hasattr(self.value, 'to_api'):
            return self.value.to_api()
        else:
            return self.value

    # TODO: move to rest_v1.ndb.entity
    @classmethod
    def from_ndb_value(cls, value, ndb_property=None, indexed=None):
        # lazy load to avoid circular import
        from .entity import Entity
        from .key import Key

        self = cls()

        if value is None:
            self.api_prop_name = 'nullValue'

        elif isinstance(value, bool):
            self.api_prop_name = 'booleanValue'
        elif isinstance(value, (int, long)):
            self.api_prop_name = 'integerValue'
        elif isinstance(value, float):
            self.api_prop_name = 'doubleValue'

        elif isinstance(value, (date, datetime, time)):
            if isinstance(value, time):
                value = ndb._time_to_datetime(value)

            value = value.strftime(TIMESTAMP_FORMAT)

            self.api_prop_name = 'timestampValue'

        elif isinstance(value, ndb.Key):
            value = Key.from_ndb_key(value)
            self.api_prop_name = 'keyValue'

        elif isinstance(value, basestring):
            value = unicode(value)
            self.api_prop_name = 'stringValue'

        elif isinstance(value, ndb.GeoPt):
            value = LatLng.from_ndb_value(value)
            self.api_prop_name = 'geoPointValue'

        elif isinstance(value, ndb.Model):
            value = Entity.from_ndb_model_instance(value)
            self.api_prop_name = 'entityValue'

        elif isinstance(value, dict):
            value = Entity(data=value)
            self.api_prop_name = 'entityValue'

        elif isinstance(value, list):
            value = ArrayValue(*map(cls.from_ndb_value, value))
            self.api_prop_name = 'arrayValue'

        elif isinstance(value, users.User):
            data = {
                'user_id': value.user_id(),
                'email': value.email(),
                'auth_domain': value.auth_domain(),
            }
            if value.federated_identity():
                data.update({
                    'federated_identity': value.federated_identity(),
                    'federated_provider': value.federated_provider(),
                })

            value = Entity(data={name: Value.from_ndb_value(value, indexed=False) for name, value in data.items()})

            self.api_prop_name = 'entityValue'

            self.meaning = 20

        else:
            raise NotImplementedError('Unknown value type for property {!r}, value: {!r}'.format(ndb_property, value))

        self.value = value
        self.indexed = ndb_property._indexed if ndb_property is not None else indexed

        return self

class ArrayValue:
    def __init__(self, *subvalues):
        self.subvalues = subvalues

    @classmethod
    def from_api(cls, *api_subvalues):
        return cls(*[Value.from_api(api_subvalue) for api_subvalue in api_subvalues])

    def to_api_value(self):
        return {
            'values': [subvalue.to_api() for subvalue in self.subvalues],
        }

class LatLng:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_api(cls, **kwargs):
        return cls(**kwargs)

    # TODO: move to rest_v1.ndb
    def to_ndb_value(self):
        return ndb.GeoPt(self.latitude, self.longitude)

    def to_api_value(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    # TODO: move to rest_v1.ndb
    @classmethod
    def from_ndb_value(cls, value):
        return cls(value.lat, value.lon)
