from ..errors import MalformedObjectError

from .entity import Entity, EntityResult
from .filter import Filter
from .order import PropertyOrder
from .reference import KindExpression, PropertyReference


class Query:
    @classmethod
    def from_api(cls, projection=None, kind=None, filter=None, order=None, distinctOn=None, startCursor=None, endCursor=None, offset=None, limit=None):
        self = cls()

        self.projection = [ProjectionElement.from_api(**projection_element) for projection_element in projection] if projection else None

        if kind is not None and len(kind) > 1:
            raise MalformedObjectError('Currently at most 1 kind may be specified.', prop='kind')
        self.kind = KindExpression.from_api(**kind[0])

        self.filter = Filter.from_api(**filter) if filter else None

        self.order = PropertyOrder.from_api(**order) if order else None

        self.group_by = [PropertyReference.from_api(**distinct_element) for distinct_element in distinctOn] if distinctOn else None

        self.start_cursor = startCursor
        self.end_cursor = endCursor

        self.offset = offset
        self.limit = limit

        return self

    @property
    def ancestor_key(self):
        if not self.filter:
            return None

        ancestor_filter = self.filter.get_ancestor_filter()
        return ancestor_filter.value.value if ancestor_filter else None


class ProjectionElement:
    def __init__(self, property):
        self.property = property

    @classmethod
    def from_api(cls, property=None):
        return cls(PropertyReference.from_api(**property))


class ResultType:
    FULL = 'FULL'
    PROJECTION = 'PROJECTION'
    KEY_ONLY = 'KEY_ONLY'

class MoreResultsType:
    NOT_FINISHED = 'NOT_FINISHED'
    MORE_RESULTS_AFTER_LIMIT = 'MORE_RESULTS_AFTER_LIMIT'
    MORE_RESULTS_AFTER_CURSOR = 'MORE_RESULTS_AFTER_CURSOR'
    NO_MORE_RESULTS = 'NO_MORE_RESULTS'


class QueryResultBatch:
    def __init__(self, query, entities, entity_cursors, more_results, skipped_results=0, skipped_cursor=None, last_cursor=None, snapshot_version=None):
        self.query = query

        self.skipped_results = skipped_results
        self.skipped_cursor = skipped_cursor

        if self.query.projection:
            self.result_type = ResultType.PROJECTION
        else:
            self.result_type = ResultType.FULL
        # KEY_ONLY-queries is not currently supported by datastore REST API v1 protocol (??? why ???)

        self.entity_results = [
            EntityResult(
                entity,
                version = snapshot_version,
                cursor = cursor,
            ) for entity, cursor in zip(entities, entity_cursors or [None] * len(entities))
        ]

        self.last_cursor = last_cursor or (entity_cursors[-1] if entity_cursors and len(entity_cursors) > 0 else None)

        if more_results:
            if self.query.end_cursor:
                self.more_results_type = MoreResultsType.MORE_RESULTS_AFTER_CURSOR
            else: # elif self.query.limit:
                self.more_results_type = MoreResultsType.MORE_RESULTS_AFTER_LIMIT
        else:
            self.more_results_type = MoreResultsType.NO_MORE_RESULTS

        self.snapshot_version = snapshot_version

    def to_api(self):
        res = {
            'skippedResults': self.skipped_results,

            'entityResults': [entity_result.to_api() for entity_result in self.entity_results],
            'entityResultType': self.result_type,

            'endCursor': self.last_cursor,
            'moreResults': self.more_results_type,
        }

        if self.skipped_results > 0:
            res['skippedCursor'] = self.skipped_cursor

        return {
            'batch': res,
        }


class LookupResult:
    def __init__(self, keys, entities):
        self.results = zip(keys, entities)

    def to_api(self):
        res = {
            'found': [],
            'missing': [],
        }

        for key, entity in self.results:
            if entity:
                res['found'].append(entity.to_api())
            else:
                res['missing'].append(EntityResult(Entity(key=key)).to_api())

        return res
