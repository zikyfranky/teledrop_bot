from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from secrets_prod import BOT_TOKEN, GROUP, CHANNEL
from flow import welcome, bep20, balance, info, end, joining, forceReg, twitter_
from helper import extract_referral


updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Join Airdrop"],
        ["My Balance", "Information"],
    ]

    name = update.message.chat.first_name
    ref = extract_referral(update.message.text)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    m_welcome = welcome % name

    m_welcome = m_welcome + "\n\nYou were referred by user with id %s" % ref if ref else m_welcome + ""
    
    update.message.reply_text(m_welcome, reply_markup=reply_markup)

def join(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Registration"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(joining, reply_markup=reply_markup, parse_mode="Markdown")

def register(update: Update, context: CallbackContext) -> None:
    try:
        context.bot.get_chat_member(chat_id=GROUP, user_id=update.message.chat.id)
        member_channel = context.bot.get_chat_member(chat_id=CHANNEL, user_id=update.message.chat.id) # Keeps returning user not fund
        keyboard = [
            ["Main Menu"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(bep20, reply_markup=reply_markup)
    except:
        keyboard = [
            ["Registration"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update.message.reply_text(forceReg, reply_markup=reply_markup)

def bep(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Main Menu"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(twitter_, reply_markup=reply_markup)

def twitter(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Join Airdrop"],
        ["My Balance", "Information"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(info, reply_markup=reply_markup)

def menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Join Airdrop"],
        ["My Balance", "Information"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🖱 Click one of the buttons below!", reply_markup=reply_markup)




start_handler = CommandHandler('start', start)
join_handler = MessageHandler(Filters.regex("^Join Airdrop$"), join)
register_handler = MessageHandler(Filters.regex("^Registration$"), register)
menu_handler = MessageHandler(Filters.regex("^Main Menu$"), menu)
bep_handler = MessageHandler(Filters.regex("^0x[a-fA-F0-9]{40}$"), bep)
twitter_handler = MessageHandler(Filters.regex("^(https:// | http://)?twitter.com/.*"), twitter)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(menu_handler)
dispatcher.add_handler(bep_handler)
dispatcher.add_handler(twitter_handler)

updater.start_polling()
