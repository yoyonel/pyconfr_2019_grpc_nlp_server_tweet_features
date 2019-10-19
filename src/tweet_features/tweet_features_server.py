"""
"""
import logging
import os
import sys

import grpc
from grpc_reflection.v1alpha import reflection  # for gRPC server reflection
from pyconfr_2019.grpc_nlp.protos import TweetFeaturesService_pb2
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2_grpc import add_TweetFeaturesServiceServicer_to_server
from pyconfr_2019.grpc_nlp.tools import rpc_server

from tweet_features.tweet_features_service import TweetFeaturesService

logger = logging.getLogger(__name__)


def serve(block=True,
          grpc_host_and_port=os.environ.get(
              "TWITTER_ANALYZER_FEATURES_GRPC_HOST_AND_PORT", '[::]:50051')):
    """
    Start a new instance of the features processing service.

    If the server can't be started, a ConnectionError exception is raised

    :param block: If True, block until interrupted.
                  If False, start the server and return directly
    :type block: bool

    :param grpc_host_and_port: Listening address of the server.
                               Defaults to the content of the
                               ``TWITTER_ANALYZER_FEATURES_GRPC_HOST_AND_PORT``
                               environment variable, or ``[::]:50052`` if not set
    :type grpc_host_and_port: str

    :return: If ``block`` is True, return nothing.
             If ``block`` is False, return the server instance
    :rtype: None | grpc.server
    """

    def _add_features_processing_service_servicer_to_server(server: grpc.Server):
        add_TweetFeaturesServiceServicer_to_server(TweetFeaturesService(), server)
        # the reflection service will be aware of "StorageService" and "ServerReflection" services.
        service_names = (
            TweetFeaturesService_pb2.DESCRIPTOR.services_by_name['TweetFeaturesService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)
        logger.info("Activate reflection on server for services: {}".format(service_names))

    return rpc_server.serve('features processing',
                            _add_features_processing_service_servicer_to_server,
                            grpc_host_and_port, block=block)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    # FIXME: parse arguments

    try:
        serve(block=True)
    except ConnectionError:
        sys.exit(1)


if __name__ == '__main__':
    main()
