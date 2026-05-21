Project Report: Multi-Language News Telegram Bot
1. Problem Statement
Staying updated with global news is often difficult for users who prefer reading in their native languages (Kazakh or Russian) when many primary news sources are in English. Additionally, users often lose track of important articles they want to read later. There was a need for a centralized, mobile-friendly tool that provides filtered news headlines with instant translation and a saving mechanism.

2. Solution Overview
We developed an asynchronous Telegram bot using the aiogram framework. The bot connects to the NewsAPI to fetch real-time headlines. To solve the language barrier, we implemented a translation layer using the deep-translator library. For data persistence, we utilized a JSON-based database system that stores user preferences (language and name) and a list of "Favorite" articles, ensuring that information is not lost when the bot restarts.

3. Simple System Design
The system follows a modular architecture to separate concerns:

Bot UI Layer (handlers.py, keyboards.py): Manages user interaction through commands and inline buttons.

Service Layer (news.py, translator.py): Handles external API communication and data processing.

Data Layer (requests.py, data.json): Manages local file I/O to ensure persistence.

4. Challenges Faced

Asynchronous Integration: Combining the asynchronous aiogram framework with external API calls required careful management of aiohttp sessions to prevent blocking the bot.

Data Consistency: Ensuring that data.json was correctly updated across different user sessions without corrupting the file was solved by implementing robust read/write functions with exception handling.

Localization: Translating dynamic content from the API while maintaining a static menu in multiple languages required a hybrid approach using a local lexicon and a live translator.

5. Team Contributions

Tair: Set up the initial bot architecture and project structure. Developed the core handlers and integrated the NewsAPI. Finalized the UI localization logic within data.json.
Ardak: Implemented the news categorization logic and the NewsTranslator class. Utilized OOP principles (inheritance from BaseProcessor) to create a reusable translation engine.
Akylzhan: Focused on the Data Persistence requirement. Developed the "Favorites" system, including the logic for adding, retrieving, and clearing articles within the JSON database.