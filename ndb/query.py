from google.appengine.ext import ndb

from ..api_objects.query import QueryResultBatch

from .ext.query import execute_query
from .filter import filter_to_ndb_node
from .entity import entity_from_ndb_model_instance
from .key import key_to_ndb_key
from .order import orders_to_datastore_order


def do_gql_query():
    raise NotImplementedError('GQL queries are not implemented yet.')

def do_query(query, partition, options):
    kind_name = query.kind.name

    ancestor_key = query.ancestor_key
    ancestor_ndb_key = key_to_ndb_key(ancestor_key, app=partition.app) if ancestor_key else None
    filter_ndb_node = filter_to_ndb_node(query.filter) if query.filter else None

    order_datastore_obj = orders_to_datastore_order(query.order) if query.order else None

    projection_property_names = [projection_element.name for projection_element in query.projection] if query.projection else None

    group_by_property_names = [group_element.name for group_element in query.group_by] if query.group_by else None

    ndb_query = ndb.Query(
        app = partition.app,
        namespace = partition.namespace,

        kind = kind_name,
        ancestor = ancestor_ndb_key,

        filters = filter_ndb_node,
        orders = order_datastore_obj,
        projection = projection_property_names,
        group_by = group_by_property_names,

        default_options = options.get_options() if options else None,
    )

    options = ndb.QueryOptions(
        start_cursor = ndb.Cursor(urlsafe=query.start_cursor) if query.start_cursor else None,
        end_cursor = ndb.Cursor(urlsafe=query.end_cursor) if query.end_cursor else None,
        limit = query.limit,
        offset = query.offset,
    )

    entities, batches = execute_query(ndb_query, options=options, record_batches=True)
    first_batch, last_batch = (batches[0], batches[-1]) if len(batches) > 0 else (None, None)

    arbitrary_cursor = first_batch.start_cursor if first_batch else None
    arbitrary_cursor = arbitrary_cursor or first_batch.end_cursor if first_batch else None
    arbitrary_cursor = arbitrary_cursor or last_batch.start_cursor if last_batch else None
    arbitrary_cursor = arbitrary_cursor or last_batch.end_cursor if last_batch else None

    return QueryResultBatch(
        query = query,
        entities = [entity_from_ndb_model_instance(entity, app=partition.app) for entity in entities],
        #entity_cursors = None, # not implemented, as the only way to get this (as I see) is very expensive (datastore_query.Batch.cursor do separate rpc to get the each cursor)
        entity_cursors = [arbitrary_cursor.urlsafe() if arbitrary_cursor else None] * len(entities),
        more_results = last_batch.more_results if last_batch else False,
        skipped_results = first_batch.skipped_results if first_batch else None,
        skipped_cursor = first_batch.start_cursor.urlsafe() if first_batch and first_batch.start_cursor else None, # TODO: not work currently (why??)
        last_cursor = last_batch.end_cursor.urlsafe() if last_batch and last_batch.end_cursor else None,
    )
