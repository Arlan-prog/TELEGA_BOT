# Multi-language Telegram News Bot

Telegram bot built with Python and aiogram. It fetches headlines from NewsAPI, translates article titles and descriptions, supports English, Russian, and Kazakh, and stores user preferences and saved articles in a local JSON file.

## Requirements

- Python 3.10 or newer
- A Telegram bot token from BotFather
- A NewsAPI key

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in `BOT_TOKEN` and `NEWS_API_KEY`.
4. Start the bot: `python run.py`.

The `.env` file and `app/database/users.json` are ignored by Git. Do not commit real credentials or user data.

## Data

Categories and translations live in `app/database/data.json`. User profiles and favorites are written to `app/database/users.json`. This JSON storage is intended for a small, single-process learning project; use a database for concurrent or multi-instance deployment.

## Commands

- `/start` opens the main menu.
- `/get_news` returns a news article.
- `/get_help` shows help.
- `/settings` opens user settings.
