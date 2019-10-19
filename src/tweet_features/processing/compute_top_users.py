from operator import itemgetter
from typing import Iterator

from pandas import DataFrame

from tweet_features.models.TopUser import TopUser


def gen_compute_top_users(
        ts_tweets: DataFrame,
        reverse: bool = True
) -> Iterator[TopUser]:
    """

    Args:
        ts_tweets:
        reverse:

    Returns:

    """
    # sort users by numbers of tweets
    sorted_users = sorted(
        [(name, len(group)) for name, group in ts_tweets.groupby('user_id')],
        key=itemgetter(1),
        reverse=reverse
    )
    for user_id, nb_tweets in sorted_users:
        yield TopUser(user_id=int(user_id), nb_tweets=nb_tweets)
