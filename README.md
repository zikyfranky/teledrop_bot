# A basic full-fledged airdrop bot for telegram, built with Python

## First Steps

[/bot](https://github.com/zikyfranky/teledrop_bot/tree/bot_polling) - Houses the telegram bot using the polling method which is never recommended if you have large users;

1. Clone the branch `git clone https://github.com/zikyfranky/teledrop_bot -b bot_polling`
2. Cd into the folder `cd bot_polling`
3. Install Requirements: `pip install -r requirements.txt`
4. Run `python bot.py`

[/webhook](https://github.com/zikyfranky/teledrop_bot/tree/webhook) - Houses the telegram bot using the webhook method which is the recommended way to go;

1. Clone the branch `git clone https://github.com/zikyfranky/teledrop_bot -b webhook`
2. Cd into the folder `cd webhook`
3. Install Requirements: `pip install -r requirements.txt`
4. Run `python app.py`

[/server](https://github.com/zikyfranky/teledrop_bot/tree/server) - Houses the telegram server that points to firebase realtime database;

1. Clone the branch `git clone https://github.com/zikyfranky/teledrop_bot -b server`
2. Cd into the folder `cd server`
3. Install Requirements: `pip install -r requirements.txt`
4. Run `python app.py`
