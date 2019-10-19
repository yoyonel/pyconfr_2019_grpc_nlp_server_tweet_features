"""
"""
from itertools import islice
from pprint import pformat

import grpc
import pytest
from google.protobuf.json_format import MessageToDict
from langdetect import DetectorFactory
# https://github.com/Mimino666/langdetect
from pyconfr_2019.grpc_nlp.protos.Timeline_pb2 import Timeline
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2 import (
    ComputeGeneralSentimentOfUserRequest,
    DetectLanguageFromTweetTextRequest,
    TopUsersRequest
)
from pyconfr_2019.grpc_nlp.tools.timestamps import parse_to_timestamp
from pyconfr_2019.grpc_nlp.tools.utils import compare_containers

DetectorFactory.seed = 0


# TODO: parametrize + more tests (parameters)
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


def test_rpc_tweet_feature_detect_language(tweet_features_rpc_stub):
    detect_language_response = tweet_features_rpc_stub.DetectLanguageFromTweetText(
        DetectLanguageFromTweetTextRequest(tweet_id=776655406764613632)
    )
    errors = compare_containers(
        MessageToDict(detect_language_response),
        {
            'language': 'pt',
            'score': 0.5714287161827087,
            'languageName': 'Portuguese',
            'text': 'Cinéma (porno) de plein air 🙃 https://t.co/I6qGD4LwrL',
        }
    )
    assert not errors, 'erroneous results spotted:\n\t{}'.format(pformat(errors))


def test_raise_exception_on_unknow_tweet_for_detect_language(tweet_features_rpc_stub):
    tweet_id = 123456789
    with pytest.raises(grpc.RpcError,
                       match="Can't find a tweet with tweet_id={} !".format(tweet_id)):
        tweet_features_rpc_stub.DetectLanguageFromTweetText(
            DetectLanguageFromTweetTextRequest(tweet_id=tweet_id)
        )


def test_raise_exception_on_unknow_tweet_for_general_sentiment(tweet_features_rpc_stub):
    user_id = 123456789
    with pytest.raises(grpc.RpcError,
                       match="Can't find tweets from user with id={} !".format(user_id)):
        tweet_features_rpc_stub.ComputeGeneralSentimentOfUser(
            ComputeGeneralSentimentOfUserRequest(user_id=user_id)
        )
