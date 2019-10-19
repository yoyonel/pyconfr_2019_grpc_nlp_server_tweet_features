from pydantic import BaseModel


class TopUser(BaseModel):
    user_id: int
    nb_tweets: int
