from pprint import pformat

import grpc
import pytest
from google.protobuf.json_format import MessageToDict
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2 import ComputeGeneralSentimentOfUserRequest
from pyconfr_2019.grpc_nlp.tools.utils import compare_containers


def test_rpc_tweet_feature_general_sentiment(tweet_features_rpc_stub):
    general_sentiment_response = tweet_features_rpc_stub.ComputeGeneralSentimentOfUser(
        ComputeGeneralSentimentOfUserRequest(user_id=592843104)
    )

    expected_result = {
        'sentiment': {
            'polarity': 0.17984959483146667,
            'subjectivity': 0.20130081474781036
        },
        'timeline': {
            'start': '1473918878000',
            'end': '1474017151000'
        },
        'nbTweets': '41'
    }
    errors = compare_containers(MessageToDict(general_sentiment_response),
                                expected_result)
    assert not errors, 'erroneous results spotted:\n\t{}'.format(pformat(errors))


def test_raise_exception_on_unknown_tweet_for_general_sentiment(tweet_features_rpc_stub):
    user_id = 123456789
    with pytest.raises(grpc.RpcError,
                       match="Can't find tweets from user with id={} !".format(user_id)):
        tweet_features_rpc_stub.ComputeGeneralSentimentOfUser(
            ComputeGeneralSentimentOfUserRequest(user_id=user_id)
        )
