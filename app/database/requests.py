import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

def _read() -> dict:
    try:
        if not os.path.exists(DATA_FILE):
            return {"users": {}, "categories": [], "lexicon": {}}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Database Read Error: {e}")
        return {"users": {}, "categories": [], "lexicon": {}}

def _write(data: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Database Write Error: {e}")


async def get_text(lang: str, key: str) -> str:
    data = _read()
    lexicon = data.get("lexicon", {})
    lang_data = lexicon.get(lang, lexicon.get("english", {}))
    return lang_data.get(key, key)

async def add_user(tg_id: int, name: str = "No name", language: str = "english") -> None:
    data = _read()
    key = str(tg_id)
    if key not in data["users"]:
        data["users"][key] = {
            "tg_id": tg_id,
            "name": name,
            "language": language
        }
        _write(data)

async def get_user(tg_id: int) -> dict | None:
    data = _read()
    return data["users"].get(str(tg_id))

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
    data = _read()
    return data.get("categories", [])

async def get_category_by_id(category_id: int) -> dict | None:
    data = _read()
    for cat in data["categories"]:
        if cat["id"] == category_id:
            return cat
    return None

async def add_to_favorites(tg_id: int, article: dict, category_id: int) -> bool:
    data = _read()
    key = str(tg_id)
    if key not in data["users"]:
        return False
    
    favorites = data["users"][key].setdefault("favorites", [])
    if any(f.get("url") == article.get("url") for f in favorites):
        return False
    
    favorites.append({
        "title":       article.get("title", "No title"),
        "description": article.get("description", ""),
        "url":         article.get("url", ""),
        "source":      article.get("source", {}).get("name", ""),
        "category_id": category_id
    })
    _write(data)
    return True

async def get_favorites(tg_id: int) -> list[dict]:
    data = _read()
    return data["users"].get(str(tg_id), {}).get("favorites", [])

async def remove_from_favorites(tg_id: int, index: int) -> bool:
    data = _read()
    key = str(tg_id)
    favorites = data["users"].get(key, {}).get("favorites", [])
    if 0 <= index < len(favorites):
        favorites.pop(index)
        data["users"][key]["favorites"] = favorites
        _write(data)
        return True
    return False

async def clear_favorites(tg_id: int) -> None:
    data = _read()
    key = str(tg_id)
    if key in data["users"]:
        data["users"][key]["favorites"] = []
        _write(data)


