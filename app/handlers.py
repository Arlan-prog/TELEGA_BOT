import html
import random
from urllib.parse import urlsplit

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.news import get_latest_news
from app.translator import LANG_CODE_MAP, translator
import app.keyboards as kb
import app.database.requests as rq

router = Router()


async def get_user_lang(tg_id: int) -> str:
    user = await rq.get_user(tg_id)
    return user["language"] if user else "english"



@router.message(CommandStart())
async def command_start_handler(message: Message):
    await rq.add_user(message.from_user.id, name=message.from_user.first_name)
    lang = await get_user_lang(message.from_user.id)
    user = await rq.get_user(message.from_user.id)
    name = user.get("name", message.from_user.first_name)
    hello_text = await rq.get_text(lang, "hello")
    intro_text = await rq.get_text(lang, "intro")

    await message.answer(f"{hello_text}, {name}!\n{intro_text}", reply_markup=await kb.get_main_keyboard(lang))



@router.callback_query(F.data == 'to_main')
async def to_main_menu(callback: CallbackQuery):
    await callback.answer()
    lang = await get_user_lang(callback.from_user.id)
    menu_label = await rq.get_text(lang, "main_menu_label")
    await callback.message.edit_text(text=menu_label, reply_markup=await kb.get_main_keyboard(lang))



@router.callback_query(F.data == 'get_categories')
async def show_categories(callback: CallbackQuery):
    await callback.answer()
    lang = await get_user_lang(callback.from_user.id)
    prompt = await rq.get_text(lang, "choose_cat")
    
    await callback.message.edit_text(
        text=prompt,
        reply_markup=await kb.inline_categories(lang)
    )



async def format_article(lang: str, article: dict, category: dict | None) -> str:
    translated = await translator.translate_article(article, lang)
    category = category or {"name": "News", "translations": {}}
    display_name = category.get("translations", {}).get(lang, category["name"])
    title = translated.get("title") or await rq.get_text(lang, "no_title")
    description = translated.get("description") or ""
    source = article.get("source", "")
    if isinstance(source, dict):
        source = source.get("name", "")

    parts = [f"📂 <b>{html.escape(str(display_name))}</b>", ""]
    parts.append(f"<b>{html.escape(str(title))}</b>")
    if source:
        parts.append(f"📡 <i>{html.escape(str(source))}</i>")
    if description:
        clean_description = str(description)[:800]
        parts.append(html.escape(clean_description))
    url = str(article.get("url") or "")
    parsed_url = urlsplit(url)
    if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
        safe_url = html.escape(url, quote=True)
        read_more = html.escape(await rq.get_text(lang, "read_more"))
        parts.append(f'<a href="{safe_url}">{read_more}</a>')
    return "\n\n".join(parts)


@router.message(Command("get_news"))
async def message_get_news(message: Message):

    category = await rq.get_category_by_id(1)
    lang = await get_user_lang(message.from_user.id)

    if not category:
        await message.answer(await rq.get_text(lang, "error_gen_not_found"))
        return

    articles = await get_latest_news(category_id=category["id"])
    
    if articles:
        article = random.choice(articles)
        text = await format_article(lang, article, category)
        _last_article[message.from_user.id] = {'article': article, 'category_id': category["id"]}
        
        await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=await kb.category_news_keyboard(lang, category["id"])
        )
    else:
        await message.answer(await rq.get_text(lang, "no_news_available"), reply_markup=await kb.get_main_keyboard(lang))

    
@router.callback_query(F.data.startswith('category_'))
async def show_category_news(callback: CallbackQuery):
    await callback.answer()
    
    cat_id = int(callback.data.split('_')[1])
    category = await rq.get_category_by_id(cat_id)
    lang = await get_user_lang(callback.from_user.id)
    
    if not category:
        await callback.message.answer(await rq.get_text(lang, "error_gen_not_found"))
        return
    
    articles = await get_latest_news(category_id=category["id"])

    if articles:
        article = random.choice(articles)
        _last_article[callback.from_user.id] = {'article': article, 'category_id': category["id"]}
        text = await format_article(lang, article, category)
        
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=await kb.category_news_keyboard(lang, category["id"])
        )
    else:
        await callback.message.edit_text(
            text=await rq.get_text(lang, "no_news_available"),
            reply_markup=await kb.inline_categories(lang)
        )


@router.callback_query(F.data.startswith('morecat_'))
async def handle_more_news(callback: CallbackQuery):
    await callback.answer()
    
    category_id = int(callback.data.split('_')[1])
    category = await rq.get_category_by_id(category_id)
    lang = await get_user_lang(callback.from_user.id)
    
    articles = await get_latest_news(category_id=category_id)

    if articles:
        article = random.choice(articles)
        _last_article[callback.from_user.id] = {'article': article, 'category_id': category_id}
        text = await format_article(lang, article, category)

        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=await kb.category_news_keyboard(lang, category_id)
        )
    else:
        await callback.message.edit_text(
            text=await rq.get_text(lang, "no_news_available"),
            reply_markup=await kb.inline_categories(lang)
        )


@router.callback_query(F.data == 'settings')
async def show_settings(callback: CallbackQuery):
    await callback.answer()
    lang = await get_user_lang(callback.from_user.id)
    settings_text = await rq.get_text(lang, "settings")
    await callback.message.edit_text(text=settings_text, reply_markup=await kb.get_settings_keyboard(lang))


@router.message(Command("settings"))
async def command_settings_handler(message: Message):
    lang = await get_user_lang(message.from_user.id)
    settings_text = await rq.get_text(lang, "settings")
    await message.answer(text=settings_text, reply_markup=await kb.get_settings_keyboard(lang))


@router.callback_query(F.data == 'change_language')
async def select_language(callback: CallbackQuery):
    await callback.answer()
    lang = await get_user_lang(callback.from_user.id)
    header = await rq.get_text(lang, "lang_header")
    await callback.message.edit_text(text=header, reply_markup=await kb.inline_languages(lang))


@router.callback_query(F.data.startswith('lang_'))
async def set_language(callback: CallbackQuery):
    new_lang = callback.data.split('_', 1)[1]
    if new_lang not in LANG_CODE_MAP:
        await callback.answer(await rq.get_text(await get_user_lang(callback.from_user.id), "not_found"), show_alert=True)
        return
    await rq.update_user_language(callback.from_user.id, new_lang)
    await callback.answer(await rq.get_text(new_lang, "lang_set"))
    
    settings_label = await rq.get_text(new_lang, "settings")
    await callback.message.edit_text(text=settings_label, reply_markup=await kb.get_settings_keyboard(new_lang))


@router.callback_query(F.data == 'get_help')
async def handle_help(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    text = await rq.get_text(lang, "help_text")
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await kb.back_to_main_keyboard(lang))


@router.message(Command("get_help"))
async def command_help_handler(message: Message):
    lang = await get_user_lang(message.from_user.id)
    text = await rq.get_text(lang, "help_text")
    await message.answer(text, parse_mode="HTML")



class UserState(StatesGroup):
    wait_name = State()


@router.callback_query(F.data == 'change_name')
async def start_change_name(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(UserState.wait_name)
    await callback.message.edit_text(await rq.get_text(lang, "name_prompt"), reply_markup=await kb.get_cancel_keyboard(lang))


@router.message(UserState.wait_name)
async def renamed_user(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 64:
        lang = await get_user_lang(message.from_user.id)
        await message.answer(await rq.get_text(lang, "name_prompt"))
        return
    await rq.update_user_name(message.from_user.id, name)
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    await message.answer(await rq.get_text(lang, "name_success"))
    await message.answer(await rq.get_text(lang, "settings"), reply_markup=await kb.get_settings_keyboard(lang))


@router.callback_query(F.data == 'cancel_name_change')
async def cancel_name_change(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(await rq.get_text(lang, "settings"), reply_markup=await kb.get_settings_keyboard(lang))

@router.message(F.photo)
async def handle_photo(message: Message):
    await message.answer('Photo ID: ' + message.photo[-1].file_id)


_last_article: dict[int, dict] = {}

@router.callback_query(F.data == "favorites")
async def show_favorites(callback: CallbackQuery):
    await callback.answer()
    lang = await get_user_lang(callback.from_user.id)
    favorites = await rq.get_favorites(callback.from_user.id)
    if not favorites:
        await callback.message.edit_text(
            await rq.get_text(lang, "no_fav"),
            reply_markup=await kb.get_main_keyboard(lang)
        )
        return
    await callback.message.edit_text(
        f"<b>{await rq.get_text(lang, 'favorites')}</b>:",
        parse_mode="HTML",
        reply_markup=await kb.favorites_list_keyboard(lang, favorites)
    )

@router.callback_query(F.data.startswith("fav_read_"))
async def read_favorite(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    index = int(callback.data.split("_")[2])
    favorites = await rq.get_favorites(callback.from_user.id)
    if not 0 <= index < len(favorites):
        await callback.answer(await rq.get_text(lang, "not_found"), show_alert=True)
        return
    await callback.answer()
    article = favorites[index]
    category = await rq.get_category_by_id(article.get("category_id"))
    text = await format_article(lang, article, category)

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await kb.favorite_article_keyboard(lang, index))

@router.callback_query(F.data.startswith("fav_del_"))
async def delete_favorite(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    index   = int(callback.data.split("_")[2])
    removed = await rq.remove_from_favorites(callback.from_user.id, index)
    await callback.answer(await rq.get_text(lang, "fav_removed") if removed else await rq.get_text(lang, "not_found"), show_alert=True)
    favorites = await rq.get_favorites(callback.from_user.id)
    if not favorites:
        await callback.message.edit_text(await rq.get_text(lang, "fav_empty"), reply_markup=await kb.get_main_keyboard(lang))
        return
    await callback.message.edit_text(
        f"<b>{await rq.get_text(lang, 'favorites')}</b>",
        parse_mode="HTML",
        reply_markup=await kb.favorites_list_keyboard(lang, favorites)
    )

@router.callback_query(F.data == "fav_clear")
async def clear_all_favorites(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await rq.clear_favorites(callback.from_user.id)
    await callback.answer(await rq.get_text(lang, "fav_cleared"), show_alert=True)
    await callback.message.edit_text(await rq.get_text(lang, "fav_empty"), reply_markup=await kb.get_main_keyboard(lang))

@router.callback_query(F.data.startswith("save_fav_"))
async def save_to_favorites(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    tg_id = callback.from_user.id
    article = _last_article.get(tg_id)
    
    if not article:
        await callback.answer(await rq.get_text(lang, "fav_not_saved"), show_alert=True)
        return
    
    added = await rq.add_to_favorites(tg_id, article["article"], article["category_id"])
    if added:
        await callback.answer(await rq.get_text(lang, "fav_added"), show_alert=True)
    else:   
        await callback.answer(await rq.get_text(lang, "fav_already"), show_alert=True)