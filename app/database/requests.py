import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
logger = logging.getLogger(__name__)


def _empty_data() -> dict:
    return {"users": {}, "categories": [], "lexicon": {}}


def _read() -> dict:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        return _empty_data()
    except (json.JSONDecodeError, OSError) as error:
        logger.warning("Could not read bot data: %s", error)
        return _empty_data()

    if not isinstance(data, dict):
        logger.warning("Bot data file has an unexpected format")
        return _empty_data()
    data.setdefault("users", {})
    data.setdefault("categories", [])
    data.setdefault("lexicon", {})
    if not isinstance(data["users"], dict):
        data["users"] = {}
    if not isinstance(data["categories"], list):
        data["categories"] = []
    if not isinstance(data["lexicon"], dict):
        data["lexicon"] = {}
    return data


def _write(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=DATA_FILE.parent, delete=False) as data_file:
            json.dump(data, data_file, ensure_ascii=False, indent=2)
            data_file.write("\n")
            temporary_name = data_file.name
        os.replace(temporary_name, DATA_FILE)
    except OSError as error:
        logger.exception("Could not save bot data: %s", error)
        raise
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


async def get_text(lang: str, key: str) -> str:
    data = _read()
    lexicon = data["lexicon"]
    lang_data = lexicon.get(lang, lexicon.get("english", {}))
    return lang_data.get(key, key)


async def add_user(tg_id: int, name: str = "No name", language: str = "english") -> None:
    data = _read()
    key = str(tg_id)
    if key not in data["users"]:
        data["users"][key] = {"tg_id": tg_id, "name": name, "language": language}
        _write(data)


async def get_user(tg_id: int) -> dict | None:
    return _read()["users"].get(str(tg_id))


async def update_user_language(tg_id: int, language: str) -> None:
    data = _read()
    key = str(tg_id)
    if key in data["users"]:
        data["users"][key]["language"] = language
        _write(data)


async def update_user_name(tg_id: int, name: str) -> None:
    data = _read()
    key = str(tg_id)
    if key in data["users"]:
        data["users"][key]["name"] = name
        _write(data)


async def get_categories() -> list[dict]:
    return _read()["categories"]


async def get_category_by_id(category_id: int) -> dict | None:
    return next(
        (category for category in _read()["categories"] if category.get("id") == category_id),
        None,
    )


async def add_to_favorites(tg_id: int, article: dict, category_id: int) -> bool:
    data = _read()
    user = data["users"].get(str(tg_id))
    if user is None:
        return False

    favorites = user.setdefault("favorites", [])
    article_url = article.get("url")
    if article_url and any(favorite.get("url") == article_url for favorite in favorites):
        return False

    source = article.get("source", "")
    if isinstance(source, dict):
        source = source.get("name", "")
    favorites.append({
        "title": article.get("title") or "No title",
        "description": article.get("description") or "",
        "url": article_url or "",
        "source": source,
        "category_id": category_id,
    })
    _write(data)
    return True


async def get_favorites(tg_id: int) -> list[dict]:
    user = _read()["users"].get(str(tg_id), {})
    favorites = user.get("favorites", [])
    return favorites if isinstance(favorites, list) else []


async def remove_from_favorites(tg_id: int, index: int) -> bool:
    data = _read()
    user = data["users"].get(str(tg_id))
    if user is None:
        return False
    favorites = user.get("favorites", [])
    if not isinstance(favorites, list) or not 0 <= index < len(favorites):
        return False
    favorites.pop(index)
    _write(data)
    return True


async def clear_favorites(tg_id: int) -> None:
    data = _read()
    user = data["users"].get(str(tg_id))
    if user is not None:
        user["favorites"] = []
        _write(data)
