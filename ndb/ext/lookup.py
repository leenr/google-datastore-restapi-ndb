from google.appengine.ext import ndb

from .context import ext_context


@ndb.tasklet
def get_key_async(key, force_app=None, context=ext_context, **ctx_options):
    if force_app:
        key = ndb.Key(pairs=key.pairs(), app=force_app)

    res = yield context.get(key, **ctx_options)
    raise ndb.Return(res)

def get_key(self, *args, **kwargs):
    return get_key_async(*args, **kwargs).get_result()
