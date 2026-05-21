# Multi-Language News Telegram Bot

## Project Description
This is a feature-rich Telegram bot developed in Python using the **aiogram** framework. The bot provides users with real-time global news headlines across multiple categories (Sports, Technology, Business, etc.). 

Key highlights include a custom-built translation engine that supports English, Kazakh, and Russian, and a persistence layer using JSON to save user preferences and favorite articles.

## Features
* **Real-time News:** Fetches the latest headlines using the NewsAPI integration.
* **Categorized Browsing:** Users can filter news by specific topics.
* **Multi-language Interface:** The entire bot UI and all news articles can be translated into English, Russian, or Kazakh.
* **Favorites System:** Save interesting articles to a personal list and manage them (view or delete).
* **Persistent Storage:** User data, language settings, and favorites are stored locally in a JSON database.
* **Interactive UI:** Uses Inline Keyboards for seamless navigation and Finite State Machines (FSM) for user inputs.

## Technologies Used
* **Language:** Python 3.x
* **Framework:** `aiogram` (Asynchronous Telegram Bot API)
* **Translation:** `deep-translator` (Google Translate API)
* **Data Handling:** `json` for data persistence and `aiohttp` for async API requests.
* **Environment Management:** `python-dotenv` for securing API credentials.

## Project Structure
TELEGRAM_BOT/<br />
├── app/<br />
│   ├── database/<br />
│   │   ├── data.json       # JSON database for users/news<br />
│   │   └── requests.py     # Database logic (CRUD operations)<br />
│   ├── handlers.py         # Bot message/callback handlers<br />
│   ├── keyboards.py        # Inline and Reply keyboards<br />
│   ├── news.py             # NewsAPI integration logic<br />
│   └── translator.py       # Translation logic (OOP-based)<br />
├── .env                    # API Tokens (Hidden)<br />
├── .gitignore              # Git exclusion rules<br />
├── config.py               # Configuration loader<br />
├── README.md               # Project documentation<br />
├── requirements.txt        # Project dependencies<br />
└── run.py                  # Entry point to start the bot<br />

## Installation & Setup
1. Clone the Repository:<br />
git clone https://github.com/SleepWalker348/telegram_bot.git<br />
cd telegram_bot
2. Create a Virtual Environment:<br />
python -m venv .venv<br />
Activate (Windows):<br />
.venv\Scripts\activate<br />
Activate (Mac/Linux):<br />
source .venv/bin/activate<br />
3. Install Dependencies:<br />
pip install -r requirements.txt<br />
4. Set Up API Keys:<br />
Create a .env file in the root directory:<br />
BOT_TOKEN=your_telegram_bot_token<br />
NEWS_API_KEY=your_news_api_key<br />

## How to Run
python run.py

## Recent Changes
* **translator.py** — Simplified `translate_text` method by removing the unnecessary intermediate variable and merging into a single return statement. Removed redundant `try/except` block from `translate_article` since error handling is already done inside `translate_text`.
* **database/requests.py** — Replaced hardcoded Windows-only path with a cross-platform solution using `os.path.dirname` and `os.path.join` so the bot runs correctly on Windows, Mac, and Linux.

## Team Member Roles
Tair: Developed the bot base, integrated NewsAPI, created core keyboards/handlers, and implemented final UI localizations.  
Ardak: Implemented the news-by-category logic, managed the JSON database structure, and integrated the NewsTranslator class.  
Akylzhan: Developed the "Favorites" management system, including logic for saving, viewing, and clearing saved articles.