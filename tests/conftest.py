import codecs
import functools
import json
import os
import socket
from contextlib import closing
from dataclasses import dataclass

from pyconfr_2019.grpc_nlp.protos import TweetFeaturesService_pb2_grpc

from tweet_features.tweet_features_server import serve

try:
    import grpc
except ImportError:
    raise ModuleNotFoundError("grpc is needed in order to "
                              "launch RPC server (`pip install .[grpc]`)")
import mongomock
import pytest
from bson import json_util

# Code highly inspired from pytest-mongodb
# https://github.com/mdomke/pytest-mongodb/blob/develop/pytest_mongodb/plugin.py
_cache = {}
_server_instance = None


@pytest.fixture(scope='function')
def mongodb(pytestconfig):
    def make_mongo_client():
        return mongomock.MongoClient()

    @dataclass
    class MongoWrapper:
        def get_db(self, fixture_name: str = None,
                   dbname: str = 'twitter_analyzer'):
            client = make_mongo_client()

            db = client[dbname]

            self.clean_database(db)

            if fixture_name is not None:
                self.load_fixtures(db, fixture_name)

            return db

        @staticmethod
        def load_fixtures(db: mongomock.Database, fixture_name: str):
            basedir = pytestconfig.getoption(
                'mongodb_fixture_dir') or pytestconfig.getini(
                'mongodb_fixture_dir')
            fixture_path = os.path.join(pytestconfig.rootdir, basedir,
                                        '{}.json'.format(fixture_name))

            if not os.path.exists(fixture_path):
                raise FileNotFoundError(fixture_path)

            loader = functools.partial(json.load,
                                       object_hook=json_util.object_hook)
            try:
                collections = _cache[fixture_path]
            except KeyError:
                with codecs.open(fixture_path, encoding='utf-8') as fp:
                    _cache[fixture_path] = collections = loader(fp)

            for collection, docs in collections.items():
                mongo_collection = db[collection]  # type: mongomock.Collection
                mongo_collection.insert_many(docs)

        @staticmethod
        def clean_database(db):
            for name in db.collection_names(include_system_collections=False):
                db.drop_collection(name)

    return MongoWrapper()


@pytest.fixture(scope='session', autouse=True)
def close_tweet_features_server(request):
    def stop_server():
        global _server_instance
        if _server_instance:
            _server_instance.stop(0)
            _server_instance = None

    request.addfinalizer(stop_server)


def find_free_port():
    # TODO: Move to tools package !
    # https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    def _find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('localhost', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    return _find_free_port()


@pytest.fixture(scope='module')
def free_port_for_grpc_server():
    return find_free_port()


@pytest.fixture(scope='function')
def mocked_tweet_features_rpc_server(mocker, free_port_for_grpc_server):
    """
    Spawn an instance of the tweet features service,
    only if one is not already available

    :param mocker:
    :param free_port_for_grpc_server:
    :return:
    """

    class Wrapper(object):
        @staticmethod
        def start(database=None):
            global _server_instance

            # Mock the database first
            mock_tweet_features = mocker.patch('tweet_features.tweet_features_service.StorageDatabase')

            if database:
                # Mock methods
                mock_tweet_features.return_value.__enter__.return_value = database

            if _server_instance is None:
                _server_instance = serve(block=False,
                                         grpc_host_and_port='[::]:{}'.format(free_port_for_grpc_server))

            assert _server_instance is not None

    return Wrapper()


@pytest.fixture
def tweet_features_rpc_stub(mongodb, mocked_tweet_features_rpc_server, free_port_for_grpc_server):
    """
    Create a new tweet features rpc stub and connect to the server

    Args:
        mongodb:
        mocked_tweet_features_rpc_server:
        free_port_for_grpc_server:

    Returns:

    """
    # Prepare mongo database
    db = mongodb.get_db('tweets')
    # Start storage server
    mocked_tweet_features_rpc_server.start(db)

    channel = grpc.insecure_channel('localhost:{}'.format(free_port_for_grpc_server))
    stub = TweetFeaturesService_pb2_grpc.TweetFeaturesServiceStub(channel)

    return stub
