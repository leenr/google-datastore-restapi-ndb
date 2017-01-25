class _NameReference:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_api(cls, name):
        return cls(name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


class PropertyReference(_NameReference):
    pass

class KindExpression(_NameReference):
    pass


KEY_PROPERTY_NAME = '__key__'
KEY_PROPERTY = PropertyReference(KEY_PROPERTY_NAME)
