from flask import request

from core.dashboard_apps.api import ApiResource

from .api_objects.key import Key, Partition
from .api_objects.read import ReadOptions
from .api_objects.query import Query # GqlQuery

from .ndb.lookup import lookup
from .ndb.query import do_query # do_gql_query


class Lookup(ApiResource):
    urls = ['/datastore_rest/v1/projects/<string:app>:lookup', '/datastore_rest/v1beta3/projects/<string:app>:lookup']

    def post(self, app):
        request_json = request.json

        read_options = ReadOptions.from_api(**request_json.get('readOptions', {}))
        keys = [Key.from_api(default_app=app, **key) for key in request_json['keys']]

        return lookup(keys, app=app, options=read_options).to_api()

class RunQuery(ApiResource):
    urls = ['/datastore_rest/v1/projects/<string:app>:runQuery', '/datastore_rest/v1beta3/projects/<string:app>:runQuery']

    def post(self, app):
        request_json = request.json

        read_options = ReadOptions.from_api(**request_json.get('readOptions', {}))
        partition = Partition.from_api(default_app=app, **request_json.get('partitionId', {}))

        if 'query' in request_json:
            query = Query.from_api(**request_json['query'])
            res = do_query(query, partition, options=read_options)

        #elif 'query' in read_options:
            #gql_query = GqlQuery.from_api(**request_json['gqlQuery'])
            #res = do_gql_query(gql_query, partition, options=read_options)

        return res.to_api()

ALL_RESOURCES = [Lookup, RunQuery]
