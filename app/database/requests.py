import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
USERS_FILE = BASE_DIR / "users.json"
logger = logging.getLogger(__name__)


def _empty_data() -> dict:
    return {"categories": [], "lexicon": {}}


def _read_data() -> dict:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        return _empty_data()
    except (json.JSONDecodeError, OSError) as error:
        logger.warning("Could not read bot configuration: %s", error)
        return _empty_data()

    if not isinstance(data, dict):
        return _empty_data()
    categories = data.get("categories", [])
    lexicon = data.get("lexicon", {})
    return {
        "categories": categories if isinstance(categories, list) else [],
        "lexicon": lexicon if isinstance(lexicon, dict) else {},
    }


def _read_users() -> dict:
    try:
        with USERS_FILE.open("r", encoding="utf-8") as user_file:
            users = json.load(user_file)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as error:
        logger.warning("Could not read user data: %s", error)
        return {}
    if not isinstance(users, dict):
        logger.warning("User data file has an unexpected format")
        return {}
    return users


def _write_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=USERS_FILE.parent, delete=False) as user_file:
            json.dump(users, user_file, ensure_ascii=False, indent=2)
            user_file.write("\n")
            temporary_name = user_file.name
        os.replace(temporary_name, USERS_FILE)
    except OSError as error:
        logger.exception("Could not save user data: %s", error)
        raise
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


async def get_text(lang: str, key: str) -> str:
    data = _read_data()
    lexicon = data["lexicon"]
    lang_data = lexicon.get(lang, lexicon.get("english", {}))
    return lang_data.get(key, key)


async def add_user(tg_id: int, name: str = "No name", language: str = "english") -> None:
    users = _read_users()
    key = str(tg_id)
    if key not in users:
        users[key] = {"tg_id": tg_id, "name": name, "language": language}
        _write_users(users)


async def get_user(tg_id: int) -> dict | None:
    return _read_users().get(str(tg_id))


async def update_user_language(tg_id: int, language: str) -> None:
    users = _read_users()
    user = users.get(str(tg_id))
    if user is not None:
        user["language"] = language
        _write_users(users)


async def update_user_name(tg_id: int, name: str) -> None:
    users = _read_users()
    user = users.get(str(tg_id))
    if user is not None:
        user["name"] = name
        _write_users(users)


async def get_categories() -> list[dict]:
    return _read_data()["categories"]


async def get_category_by_id(category_id: int) -> dict | None:
    return next(
        (category for category in _read_data()["categories"] if category.get("id") == category_id),
        None,
    )


async def add_to_favorites(tg_id: int, article: dict, category_id: int) -> bool:
    users = _read_users()
    user = users.get(str(tg_id))
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
    _write_users(users)
    return True


async def get_favorites(tg_id: int) -> list[dict]:
    user = _read_users().get(str(tg_id), {})
    favorites = user.get("favorites", [])
    return favorites if isinstance(favorites, list) else []


async def remove_from_favorites(tg_id: int, index: int) -> bool:
    users = _read_users()
    user = users.get(str(tg_id))
    if user is None:
        return False
    favorites = user.get("favorites", [])
    if not isinstance(favorites, list) or not 0 <= index < len(favorites):
        return False
    favorites.pop(index)
    _write_users(users)
    return True


async def clear_favorites(tg_id: int) -> None:
    users = _read_users()
    user = users.get(str(tg_id))
    if user is not None:
        user["favorites"] = []
        _write_users(users)
