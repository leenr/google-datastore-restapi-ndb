from ..api_objects.order import SortDirection

from google.appengine.datastore import datastore_query


DATASTORE_ORDER_DIRECTION_MAPPING = {
    SortDirection.ASCENDING: datastore_query.PropertyOrder.ASCENDING,
    SortDirection.DESCENDING: datastore_query.PropertyOrder.DESCENDING,
}

def order_to_datastore_order(order):
    property_name = order.property.name
    order_datastore_direction = DATASTORE_ORDER_DIRECTION_MAPPING.get(order.direction)

    return datastore_query.PropertyOrder(
        property_name,
        direction = order_datastore_direction,
    )

def orders_to_datastore_order(orders):
    datastore_orders = map(order_to_datastore_order, orders)

    if len(orders) == 0:
        return None
    elif len(orders) == 1:
        return datastore_orders[0]
    else:
        return datastore_query.CompositeOrder(datastore_orders)
