from itertools import islice
from pprint import pformat

from google.protobuf.json_format import MessageToDict
from pyconfr_2019.grpc_nlp.protos.Timeline_pb2 import Timeline
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2 import TopUsersRequest
from pyconfr_2019.grpc_nlp.tools.timestamps import parse_to_timestamp
from pyconfr_2019.grpc_nlp.tools.utils import compare_containers


def test_rpc_tweet_feature_top_users(tweet_features_rpc_stub):
    nb_top_users = 5
    # https://docs.python.org/3/library/itertools.html#itertools.islice
    top_users_response = islice(
        tweet_features_rpc_stub.TopUsers(
            TopUsersRequest(timeline=Timeline(start=parse_to_timestamp('2016/01/01'),
                                              end=parse_to_timestamp('2016/12/31')))),
        nb_top_users
    )
    expected_results = [{'nbTweets': '21', 'userId': '14344469'},
                        {'nbTweets': '23', 'userId': '1269648812'},
                        {'nbTweets': '25', 'userId': '15808647'},
                        {'nbTweets': '39', 'userId': '1236101'},
                        {'nbTweets': '41', 'userId': '592843104'}]

    errors = compare_containers(list(map(MessageToDict, top_users_response)),
                                expected_results)
    assert not errors, 'erroneous results spotted:\n\t{}'.format(pformat(errors))
