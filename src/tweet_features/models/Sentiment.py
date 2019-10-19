import datetime

from pydantic import BaseModel


class Sentiment(BaseModel):
    polarity: float
    subjectivity: float


class Timeline(BaseModel):
    start: datetime.datetime
    end: datetime.datetime


class GeneralSentiment(BaseModel):
    sentiment: Sentiment
    timeline: Timeline
    nb_tweets: int
