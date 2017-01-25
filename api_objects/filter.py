from .reference import KEY_PROPERTY, PropertyReference
from .value import Value


class Filter:
    ''' Base (abstract) class for filters '''
    @classmethod
    def from_api(cls, compositeFilter=None, propertyFilter=None):
        if compositeFilter:
            return CompositeFilter(
                op = compositeFilter['op'],
                subfilters = [
                    Filter.from_api(**subfilter) for subfilter in compositeFilter['filters']
                ],
            )
        elif propertyFilter:
            return PropertyFilter(
                by_property = PropertyReference.from_api(**propertyFilter['property']),
                op = propertyFilter['op'],
                value = Value.from_api(**propertyFilter['value']),
            )


class CompositeFilter(Filter):
    class Operator:
        AND = 'AND'
        OR = 'OR'

    def __init__(self, op, subfilters):
        self.op = op.upper()
        self.subfilters = subfilters

    def to_api(self):
        return {
            'compositeFilter': {
                'op': self.op,
                'filters': self.value.to_api(),
            }
        }

    def get_ancestor_filter(self):
        for subfilter in self.subfilters:
            ancestor_filter = subfilter.get_ancestor_filter()
            if ancestor_filter:
                return ancestor_filter
        else:
            return None


class PropertyFilter(Filter):
    class Operator:
        LESS_THAN = 'LESS_THAN'
        LESS_THAN_OR_EQUAL = 'LESS_THAN_OR_EQUAL'
        GREATER_THAN = 'GREATER_THAN'
        GREATER_THAN_OR_EQUAL = 'GREATER_THAN_OR_EQUAL'
        EQUAL = 'EQUAL'
        HAS_ANCESTOR = 'HAS_ANCESTOR'

    def __init__(self, by_property, op, value):
        self.by_property = by_property
        self.op = op.upper()
        self.value = value

    def to_api(self):
        return {
            'propertyFilter': {
                'property': self.by_property.to_api(),
                'op': self.op,
                'value': self.value.to_api(),
            }
        }

    def is_ancestor_filter(self):
        return (
            self.by_property == KEY_PROPERTY and
            self.op == self.Operator.HAS_ANCESTOR
        )

    def get_ancestor_filter(self):
        return self if self.is_ancestor_filter() else None
