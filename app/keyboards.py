from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.translator import translator, LANG_CODE_MAP
import app.database.requests as rq



async def get_main_keyboard(lang: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "get_news"), callback_data="category_1"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "categories"), callback_data="get_categories"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "favorites"), callback_data="favorites"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "settings"), callback_data="settings"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "help"), callback_data="get_help"))
    return builder.adjust(2).as_markup()


async def inline_categories(lang: str):
    categories = await rq.get_categories()
    builder = InlineKeyboardBuilder()
    
    for cat in categories:
        translated_name = cat.get("translations", {}).get(lang, cat["name"])
        builder.add(InlineKeyboardButton(text=translated_name, callback_data=f"category_{cat['id']}"))
    
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.adjust(2).as_markup()


async def category_news_keyboard(lang: str, category_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "more_news"), callback_data=f"morecat_{category_id}"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "save_fav"), callback_data=f"save_fav_{category_id}"))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "back_cat"), callback_data="get_categories")),
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.adjust(2).as_markup()


async def get_settings_keyboard(lang: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "lang_btn"), callback_data="change_language"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "name_btn"), callback_data="change_name"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.as_markup()


async def inline_languages(lang):
    lang_map = {'English': '🇺🇸', 'Kazakh': '🇰🇿', 'Russian': '🇷🇺'}
    builder = InlineKeyboardBuilder()
    for language, icon in lang_map.items():
        builder.add(InlineKeyboardButton(text=f"{icon} {await rq.get_text(language.lower(), 'lang')}", callback_data=f'lang_{language.lower()}'))
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "back"), callback_data='settings'))
    return builder.adjust(1).as_markup()


async def get_cancel_keyboard(lang: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "cancel"), callback_data="cancel_name_change", style='danger'))
    return builder.as_markup()


async def back_to_main_keyboard(lang: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.as_markup()

async def favorites_list_keyboard(lang: str, favorites: list[dict]):
    builder = InlineKeyboardBuilder()
    for i, article in enumerate(favorites):
        article = {"title": article["title"]}
        title = await translator.translate_article(article, lang)
        builder.row(InlineKeyboardButton(
            text=f"📰 {title['title']}",
            callback_data=f"fav_read_{i}"
        ))
        builder.add(InlineKeyboardButton(
            text=await rq.get_text(lang, "fav_delete"),
            callback_data=f"fav_del_{i}"
        ))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "fav_clear"), callback_data="fav_clear"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.adjust(2).as_markup()

async def favorites_keyboard(lang: str, index: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "fav_delete"), callback_data=f"fav_del_{index}"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "back_to_fav"), callback_data="favorites"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.as_markup()

async def favorite_article_keyboard(lang: str, index: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "back_to_fav"), callback_data="favorites"))
    builder.row(InlineKeyboardButton(text=await rq.get_text(lang, "main_menu_label"), callback_data="to_main"))
    return builder.as_markup()