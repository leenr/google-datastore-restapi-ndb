from google.appengine.ext import ndb

 
def _make_ext_connection():
    conn = ndb.make_connection(default_model=ndb.Expando)
    return conn

_ext_connection = _make_ext_connection()
ext_context = ndb.Context(_ext_connection)
