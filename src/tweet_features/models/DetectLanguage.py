from pyconfr_2019.grpc_nlp.tools.lang_list import lang_list
from pydantic import BaseModel, validator


class DetectLanguage(BaseModel):
    language: str
    score: float
    language_name: str

    # https://pydantic-docs.helpmanual.io/#validators
    @validator('language')
    def validator_is_in_lang_list(cls, v):
        if v not in lang_list:
            msg_err = "lang='{}' not in lang list".format(v)
            raise ValueError(msg_err)
        return v
