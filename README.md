# A basic airdrop bot for telegram, built with Python

## First Steps
Run `pip install -r requirements.txt` to install dependencies

[/bot](/bot) - Houses the telegram bot
to run, type:  `python bot/bot.py from root directory`, or `python bot.py` if you are in the bot directory

[/server](/server) - Houses the telegram server that points to firebase realtime database
to run, type:  `python server/app.py from root directory`, or `python app.py` if you are in the server directory

`bot/flow.json` is a file that holds the flow of the chatbot with keys like, `welcome, end, info, bep20` etc

`BOT_TOKEN` should be imported from `bot/secrets` and not `bot/_secrets`
