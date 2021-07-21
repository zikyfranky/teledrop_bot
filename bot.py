from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import _secrets
import flow
import helper 

updater = Updater(token=_secrets.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Join Airdrop"],
        ["My Balance", "Information"],
    ]

    name = update.message.chat.first_name
    ref = helper.extract_referral(update.message.text)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    m_welcome = flow.welcome % name

    m_welcome = m_welcome + "\n\nYou were referred by user with id %s" % ref if ref else m_welcome + ""
    
    update.message.reply_text(m_welcome, reply_markup=reply_markup)

def join(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Registration"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(flow.joining, reply_markup=reply_markup, parse_mode="Markdown")

def register(update: Update, context: CallbackContext) -> None:
    try:
        context.bot.get_chat_member(chat_id=_secrets.GROUP, user_id=update.message.chat.id)
    except:
        keyboard = [
            ["Registration"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(flow.forceReg, reply_markup=reply_markup, parse_mode="Markdown")
        return
    try:
        context.bot.get_chat_member(chat_id=_secrets.CHANNEL, user_id=update.message.chat.id) # Keeps returning user not fund
    except:
        try:
            context.bot.get_chat_administrators(chat_id=_secrets.CHANNEL)
            keyboard = [
                ["Registration"],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            update.message.reply_text(
                flow.forceReg, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            return
        
    keyboard = [
        ["Main Menu"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(flow.bep20, reply_markup=reply_markup)
    

def bep(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Main Menu"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(flow.twitter, reply_markup=reply_markup)

def twitter(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Join Airdrop"],
        ["My Balance", "Information"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(flow.info, reply_markup=reply_markup)

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
