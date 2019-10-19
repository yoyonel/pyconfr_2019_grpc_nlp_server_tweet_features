import re
from collections import defaultdict
from typing import Tuple

import pandas as pd
# https://www.regextester.com/93652
from pandas import DataFrame
from textblob import Blobber, TextBlob
from textblob_fr import PatternAnalyzer, PatternTagger

from tweet_features.models.Sentiment import GeneralSentiment, Sentiment, Timeline

pattern_regex_remove_url = r"^(http://www\.|https://www\.|http://|https://)?[a-z0-9]+([\-.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?$"
# https://docs.python.org/3/library/re.html#re.compile
prog_remove_url = re.compile(pattern_regex_remove_url)

# https://regex101.com/r/yD1lU1/1
pattern_keep_valid_letters = r"(@[A-Za-z0-9éèàê]+)|([^0-9A-Za-zéèàê \t])|(\w+://\S+)"
prog_keep_valid_letters = re.compile(pattern_keep_valid_letters)

tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())


# https://textblob.readthedocs.io/en/dev/api_reference.html#textblob.blob.TextBlob.sentiment
def get_polarity_sentiment_en(tweet_text: str) -> Tuple[float, float]:
    return tuple(TextBlob(tweet_text).sentiment)


def get_polarity_sentiment_fr(tweet_text: str) -> Tuple[float, float]:
    return tuple(tb(tweet_text).sentiment)


m_func_lang_to_polarity_sentiment = defaultdict(
    lambda: lambda _: pd.np.nan,
    {
        'en': get_polarity_sentiment_en,
        'fr': get_polarity_sentiment_fr,
    }
)


def clean_tweet(tweet_text: str) -> str:
    # remove urls
    tweet_clean_text = ' '.join(
        re.sub(prog_remove_url, " ", tweet_text).split())

    tweet_clean_text = ' '.join(
        re.sub(prog_keep_valid_letters, " ", tweet_clean_text).split())

    return tweet_clean_text


def compute_general_sentiment(ts_tweets: DataFrame) -> GeneralSentiment:
    ts_tweets = ts_tweets.copy()

    ts_tweets['clean_text'] = ts_tweets['text'].apply(clean_tweet)

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    ts_tweets[['polarity', 'subjectivity']] = ts_tweets.apply(
        lambda row: m_func_lang_to_polarity_sentiment[row['lang']](
            row['clean_text']),
        axis=1,
        result_type="expand"
    )

    mean_sentiments = ts_tweets[['polarity', 'subjectivity']].mean()

    return GeneralSentiment(
        sentiment=Sentiment(
            polarity=mean_sentiments['polarity'],
            subjectivity=mean_sentiments['subjectivity'],
        ),
        timeline=Timeline(
            start=ts_tweets.index[-1],
            end=ts_tweets.index[0],
        ),
        nb_tweets=len(ts_tweets)
    )
