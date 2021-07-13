import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from secrets_prod import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Join Airdrop", callback_data='1')],
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
    ]
    context.bot.send_message(update.effective_chat.id, text="Welcome to {NAME} bot")


start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)

updater.start_polling()
