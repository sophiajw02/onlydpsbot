# onlydpsbot
Only DPS Bot is a Discord Bot that provides raiding aid for Final Fantasy XIV. Functionalities include...
* Logging events and raid dates through Google Calendars
* Searching up current tier logs through FFLogs
* Searching up characters and items from the Lodestone through XIVAPI 


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
