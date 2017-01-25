from .reference import PropertyReference


class SortDirection:
    ASCENDING = 'ASCENDING'
    DESCENDING = 'DESCENDING'

class PropertyOrder:
    @classmethod
    def from_api(cls, property, direction=SortDirection.ASCENDING):
        self = cls()

        self.property = PropertyReference.from_api(property)
        self.direction = direction

        return self
