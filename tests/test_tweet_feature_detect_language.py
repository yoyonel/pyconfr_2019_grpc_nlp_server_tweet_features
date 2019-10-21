from pprint import pformat

import grpc
import pytest
from google.protobuf.json_format import MessageToDict
from langdetect import DetectorFactory
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2 import DetectLanguageFromTweetTextRequest
from pyconfr_2019.grpc_nlp.tools.utils import compare_containers

# https://github.com/Mimino666/langdetect

DetectorFactory.seed = 0


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


def test_raise_exception_on_unknown_tweet_for_detect_language(tweet_features_rpc_stub):
    tweet_id = 123456789
    with pytest.raises(grpc.RpcError,
                       match="Can't find a tweet with tweet_id={} !".format(tweet_id)):
        tweet_features_rpc_stub.DetectLanguageFromTweetText(
            DetectLanguageFromTweetTextRequest(tweet_id=tweet_id)
        )
