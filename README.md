# Bus info bot

Telegram bot for Israel that provides real time of bus arrivals.

## Usage 
Just open the bot at Telegram, and send id of your station.
https://t.me/ilbusbot

The bot will send you anformation about buses that comes soon.
<br>
<img src="https://telegra.ph/file/35db2920175d05b717e3c.png" width=450px>

The message with lines will updated every 15 seconds untill either:
- timout 10 minutes will riached
- "Stop updating" button will pressed
- another station id will sent


## Project structure

There are two parts of project:
- The bot: provides basic bot options, such as reply to your messages. Powered by [aiogram](https://github.com/aiogram/aiogram) 
- Updater: updates messages that have been sent by bot. Powered by [Celery](https://github.com/celery/celery)
