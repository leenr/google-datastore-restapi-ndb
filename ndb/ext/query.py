from google.appengine.ext import ndb

from .context import ext_context


def iter_query(query, callback=None, pass_batch_into_callback=False, context=ext_context, options=None):
    return context.iter_query(query,
        callback = callback,
        pass_batch_into_callback = pass_batch_into_callback,
        options = options,
    )

def execute_query(query, context=ext_context, options=None, record_batches=False):
    if record_batches:
        batches = []

        def record_batches_callback(batch, i, entity):
            batches.append(batch)
            return entity

        return context.map_query(query, record_batches_callback, pass_batch_into_callback=True, options=options).get_result(), batches
    else:
        return context.map_query(query, None, options=options).get_result()
