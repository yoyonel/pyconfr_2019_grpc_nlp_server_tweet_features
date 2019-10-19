import logging
from typing import Tuple

import pycountry
import spacy
from spacy_langdetect import LanguageDetector

# https://github.com/Abhijit-2592/spacy-langdetect
from tweet_features.models.DetectLanguage import DetectLanguage

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(LanguageDetector(), name="language_detector", last=True)

logger = logging.getLogger(__name__)


def compute_detect_language(tweet_text: str) -> DetectLanguage:
    """

    Args:
        tweet_text:

    Returns:

    """

    # (pretty) slow process ...
    def detect_lang(t: str) -> Tuple[str, float]:
        lang = nlp(t)._.language
        return lang['language'], lang['score']

    language, score = detect_lang(tweet_text)
    language_name = find_language_name(language)

    return DetectLanguage(language=language, score=score, language_name=language_name)


def find_language_name(language: str) -> str:
    # => update models/message(proto)
    try:
        language_name = pycountry.languages.get(alpha_2=language).name
    except AttributeError:
        logger.warning(f"Can't find name for language={language}!")
        language_name = language
    return language_name
