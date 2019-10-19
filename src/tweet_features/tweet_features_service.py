"""
"""
import logging

import grpc
import pandas as pd
from pyconfr_2019.grpc_nlp.protos.Sentiment_pb2 import Sentiment
from pyconfr_2019.grpc_nlp.protos.Timeline_pb2 import Timeline
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2 import (
    ComputeGeneralSentimentOfUserRequest,
    ComputeGeneralSentimentOfUserResponse,
    DetectLanguageFromTweetTextRequest,
    DetectLanguageFromTweetTextResponse,
    TopUsersRequest,
    TopUsersResponse
)
from pyconfr_2019.grpc_nlp.protos.TweetFeaturesService_pb2_grpc import TweetFeaturesServiceServicer
from pyconfr_2019.grpc_nlp.tools.rpc_errors import abort_if_empty
from pyconfr_2019.grpc_nlp.tools.timestamps import unix_timestamp_ms_to_datetime

from tweet_features.dataproviders.storage_db import StorageDatabase
from tweet_features.processing.compute_general_sentiment import compute_general_sentiment
from tweet_features.processing.compute_top_users import gen_compute_top_users
from tweet_features.processing.detect_language import compute_detect_language

logger = logging.getLogger(__name__)


class TweetFeaturesService(TweetFeaturesServiceServicer):
    """
        Implementation of the TweetFeatures rpc service
    """

    def TopUsers(
            self,
            request: TopUsersRequest,
            context: grpc.ServicerContext
    ) -> TopUsersResponse:
        """
        Q: "qui sont les utilisateurs les plus présents sur une timeline Twitter ?"

        Args:
            request:
            context:

        Returns:

        """
        # timeline datetimes from request
        timeline_dt_start = unix_timestamp_ms_to_datetime(request.timeline.start)
        timeline_dt_end = unix_timestamp_ms_to_datetime(request.timeline.end)
        # retrieve tweets from database (in regard of a timeline)
        with StorageDatabase() as db:
            # retrieve tweets from database
            # https://web.archive.org/web/20140802203425/http://cookbook.mongodb.org/patterns/date_range/
            it_tweets = db.tweets.find(
                {
                    "created_at": {
                        "$gte": timeline_dt_start,
                        "$lte": timeline_dt_end,
                    }
                }
            )

            abort_details = "Can't find any tweets in timeline=[{}, {}] !".format(timeline_dt_start, timeline_dt_end)
            try:
                it_tweets = abort_if_empty(it_tweets, context, abort_details=abort_details)
            except BaseException:
                logger.error(abort_details)
                return TopUsersResponse(),

        ts_tweets = pd.DataFrame.from_records(it_tweets)

        # process feature: top users and iter on results
        for top_user in gen_compute_top_users(ts_tweets):
            # build message result
            msg_top_users_responses = TopUsersResponse(**top_user.dict())
            # send message (unidirectional stream, one_to_many)
            yield msg_top_users_responses

    def ComputeGeneralSentimentOfUser(
            self,
            request: ComputeGeneralSentimentOfUserRequest,
            context: grpc.ServicerContext
    ) -> ComputeGeneralSentimentOfUserResponse:
        """
        Q: "quel est le sentiment général des tweets (positif ou négatif) d’un utilisateur ?"

        Args:
            request:
            context:

        Returns:

        """
        # retrieve tweets from database
        with StorageDatabase() as db:
            it_tweets = db.tweets.find({"user_id": {"$eq": str(request.user_id)}})

        # abort gRPC connection and early exit if no tweets find
        abort_details = "Can't find tweets from user with id={} !".format(request.user_id)
        try:
            it_tweets = abort_if_empty(it_tweets, context, abort_details=abort_details)
        except BaseException:
            logger.error(abort_details)
            return ComputeGeneralSentimentOfUserResponse()

        ts_tweets = pd.DataFrame.from_records(it_tweets, index='created_at')

        # process feature: general sentiment from twitter user
        general_sentiment = compute_general_sentiment(ts_tweets)

        # build message result
        msg_general_sentiment = ComputeGeneralSentimentOfUserResponse(
            sentiment=Sentiment(**general_sentiment.sentiment.dict()),
            timeline=Timeline(
                start=int(general_sentiment.timeline.start.timestamp() * 1000),
                end=int(general_sentiment.timeline.end.timestamp() * 1000)
            ),
            nb_tweets=general_sentiment.nb_tweets,
        )
        # send message result (one_to_one)
        return msg_general_sentiment

    def DetectLanguageFromTweetText(
            self,
            request: DetectLanguageFromTweetTextRequest,
            context: grpc.ServicerContext
    ) -> DetectLanguageFromTweetTextResponse:
        """
        Q: "à partir du texte d’un tweet, est-il possible de deviner la langue dans lequel le tweet a été rédigé ?"

        Args:
            request:
            context:

        Returns:

        """
        # process feature: detect language from tweet id
        with StorageDatabase() as db:
            tweet = db.tweets.find_one({'tweet_id': str(request.tweet_id)})

        if tweet is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Can't find a tweet with tweet_id={} !".format(request.tweet_id))
            return DetectLanguageFromTweetTextResponse()

        tweet_text = tweet['text']
        logger.debug(f"tweet_id={request.tweet_id} => text: {tweet_text}")
        detect_language = compute_detect_language(tweet_text)
        # build message result
        msg_detect_language = DetectLanguageFromTweetTextResponse(**{**detect_language.dict(), **{'text': tweet_text}})
        # send message result (one_to_one)
        return msg_detect_language
