import asyncio
import logging

import aiohttp

from config import NEWS_API_KEY
import app.database.requests as rq

logger = logging.getLogger(__name__)
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"


async def get_latest_news(category_id: int = 1) -> list[dict]:
    category = await rq.get_category_by_id(category_id)
    if category is None:
        logger.warning("News category %s was not found", category_id)
        return []
    if not NEWS_API_KEY:
        logger.error("NEWS_API_KEY is not configured")
        return []

    params = {
        "country": "us",
        "category": category.get("api_slug", "general"),
        "pageSize": 30,
    }
    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                NEWS_API_URL,
                params=params,
                headers={"X-Api-Key": NEWS_API_KEY},
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("status") != "ok":
                    logger.warning("News API returned a non-success response")
                    return []
                return [
                    article
                    for article in data.get("articles", [])
                    if article.get("title")
                ]
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as error:
        logger.warning("Could not fetch news: %s", error)
        return []
