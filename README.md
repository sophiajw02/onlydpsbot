# onlydpsbot

## About
Only DPS Bot is a Discord Bot that provides raiding aid for Final Fantasy XIV. The bot includes functionality for...
* Google Calendars (logging events/raid dates)
* FFLogs (searching up current tier logs)
* XIVAPI (searching up characters and items from the Lodestone)


## Install dependencies: 
* discord.py
* discord.ext.menus - https://github.com/Rapptz/discord-ext-menus
* apscheduler
* aiosqlite
* aiohttp
* Google Client Library (google-api-python-client, google-auth-httplib2, google-auth-oauthlib)
* pyxivapi


## Other files:
* bot_token.0 (Discord Bot Token to be put under lib/bot/)
* credentials.json (for Google Calendar)
* calendar_id.0 (ID of Google Calendar to be used to be put under lib/cogs/)
* log_token.0 (FFLogs Token to be put under lib/cogs/)
* xivsearch_token (XIVSearch Token to be put under lib/cogs/)
