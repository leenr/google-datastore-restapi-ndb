from google.appengine.ext.ndb.google_imports import datastore_rpc

from ..errors import MalformedObjectError


class ReadConsistency:
    STRONG = 'STRONG' # ?
    EVENTUAL = 'EVENTUAL' # ?

class ReadOptions:
    @classmethod
    def from_api(cls, consistency_type=None, transaction=None):
        self = cls()

        self.consistency_type = consistency_type
        if self.consistency_type:
            self.read_policy = {
                ReadConsistency.STRONG: datastore_rpc.Configuration.STRONG_CONSISTENCY,
                ReadConsistency.EVENTUAL: datastore_rpc.Configuration.EVENTUAL_CONSISTENCY,
            }.get(consistency_type, None)

            if self.read_policy is None:
                raise MalformedObjectError('consistency_type {} is unknown'.format(consistency_type))

        self.transaction = transaction

        return

    def get_options(self):
        if self.transaction is not None:
            raise NotImplementedError('Read operations in a specified transaction are not supported')

        return datastore_rpc.Configuration(read_policy=self.read_policy)
