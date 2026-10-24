import asyncio
import logging

from deep_translator import GoogleTranslator

LANG_CODE_MAP = {
    "english": None,
    "russian": "ru",
    "kazakh": "kk",
}

logger = logging.getLogger(__name__)


class BaseProcessor:
    def __init__(self) -> None:
        self.name = "Language Processor"


class NewsTranslator(BaseProcessor):
    def __init__(self) -> None:
        super().__init__()

    async def translate_text(self, text: str, dest_lang: str) -> str:
        if not text:
            return ""
        try:
            translated = await asyncio.to_thread(
                GoogleTranslator(source="auto", target=dest_lang).translate,
                text,
            )
            return translated or text
        except Exception as error:
            logger.warning("Translation failed: %s", error)
            return text

    async def translate_article(self, article: dict, user_language: str) -> dict:
        lang_code = LANG_CODE_MAP.get(user_language.lower())
        if not lang_code:
            return article

        translated = article.copy()
        for field in ("title", "description"):
            if article.get(field):
                translated[field] = await self.translate_text(article[field], lang_code)
        return translated


translator = NewsTranslator()
