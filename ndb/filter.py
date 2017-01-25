from google.appengine.ext import ndb

from ..api_objects.filter import CompositeFilter, PropertyFilter


# _OPS set in google.appengine.ext.ndb.query
PROPERTY_FILTER_NDB_OP_MAPPING = {
    PropertyFilter.Operator.EQUAL: '=',
    PropertyFilter.Operator.GREATER_THAN: '>',
    PropertyFilter.Operator.GREATER_THAN_OR_EQUAL: '>=',
    PropertyFilter.Operator.LESS_THAN: '<',
    PropertyFilter.Operator.LESS_THAN_OR_EQUAL: '<=',
}

# also in google.appengine.ext.ndb.query
COMPOSITE_FILTER_OP_NDB_NODE_CLASS_MAPPING = {
    CompositeFilter.Operator.AND: ndb.ConjunctionNode,
    CompositeFilter.Operator.OR: ndb.DisjunctionNode,
}

def filter_to_ndb_node(qfilter):
    if isinstance(qfilter, PropertyFilter):
        if qfilter.op == PropertyFilter.Operator.HAS_ANCESTOR:
            return None # HAS_ANCESTOR filter is handled by another function. TODO: improve that

        ndb_op = PROPERTY_FILTER_NDB_OP_MAPPING.get(qfilter.op, None)
        if ndb_op is None:
            raise NotImplementedError('Unsupported property filter operation: {!r}'.format(qfilter.op))

        return ndb.FilterNode(qfilter.by_property.name, ndb_op, qfilter.value.value)

    elif isinstance(qfilter, CompositeFilter):
        # Filtering to ensure that property filter with op HAS_ANCESTOR
        subnodes = filter(lambda node: node, map(filter_to_ndb_node, qfilter.subfilters))

        # Check to ensure we don't resulted to zero-subnodes filter or "composite" filter with only one node
        if len(subnodes) == 0:
            return None
        elif len(subnodes) == 1:
            return subnodes[0]
        else:
            node_class = COMPOSITE_FILTER_OP_NDB_NODE_CLASS_MAPPING.get(qfilter.op, None)
            if node_class is None:
                raise NotImplementedError('Unsupported composite filter operation: {!r}'.format(qfilter.op))
            return node_class(*subnodes)

    else:
        raise NotImplementedError('Unsupported filter type: {!r}'.format(qfilter))
