from google.appengine.ext import ndb


class _GenericModelBase(ndb.Expando):
    @staticmethod
    def _get_kind():
        raise NotImplementedError()

    @staticmethod
    def _update_kind_map():
        # prevent ndb.Model._update_kind_map to write this models to kind map
        pass


def generic_property(name):
    return ndb.GenericProperty(name)

def generic_model(kind_name):
    class GenericModel(_GenericModelBase):
        @staticmethod
        def _get_kind():
            return kind_name

    # for debugging purposes
    GenericModel.__name__ += '__' + kind_name

    return GenericModel
