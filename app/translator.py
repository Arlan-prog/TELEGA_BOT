from deep_translator import GoogleTranslator

LANG_CODE_MAP = {
    'english': None,
    'russian': 'ru',
    'kazakh':  'kk',
}

class BaseProcessor:
    def __init__(self):
        self.name = "Language Processor"

class NewsTranslator(BaseProcessor):
    def __init__(self):
        super().__init__()

    async def translate_text(self, text: str, dest_lang: str) -> str:
        if not text:
            return ""
        try:
            return GoogleTranslator(source='auto', target=dest_lang).translate(text) or text
        except Exception as e:
            print(f"Translation Error: {e}")
            return text

    async def translate_article(self, article: dict, user_language: str) -> dict:
        lang_code = LANG_CODE_MAP.get(user_language.lower())
        if not lang_code:
            return article

        translated = article.copy()

        if article.get('title'):
            translated['title'] = await self.translate_text(article['title'], lang_code)

        if article.get('description'):
            translated['description'] = await self.translate_text(article['description'], lang_code)

        return translated

translator = NewsTranslator()