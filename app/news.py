import aiohttp

from config import NEWS_API_KEY
import app.database.requests as rq

async def get_latest_news(category_id: int = "1") -> list[dict]:
    category = await rq.get_category_by_id(category_id)
    url = (
        f"https://newsapi.org/v2/top-headlines"
        f"?country=us"
        f"&category={category.get("api_slug", "general")}"
        f"&pageSize=30"
        f"&apiKey={NEWS_API_KEY}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return [a for a in data.get("articles", []) if a.get("title")]
                else:
                    print(f"News API returned status {response.status}")
                    return []
    except Exception as e:
        print(f"News API Error: {e}") 
        return []

    