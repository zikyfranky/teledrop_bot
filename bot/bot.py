from telegram import ReplyKeyboardMarkup, Update
from telegram.chatmember import ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import _secrets
import flow
import helper 
import steps

updater = Updater(token=_secrets.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    keyboard:list = [
        ['Join Airdrop'],
        ['My Balance', 'Information']
    ]

    # get name and ID, if no name, use id
    name:str = update.message.chat.first_name
    u_id:str = update.message.chat.id
    name = name if name else u_id

    # Get referral from start 
    ref:str = helper.extract_referral(update.message.text)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    m_welcome:str = flow.welcome % name 

    m_welcome = m_welcome + '\n\nYou were referred by user with id `%s`' % ref if ref else m_welcome + ''
    
    # Reply user
    update.message.reply_text(m_welcome, reply_markup=reply_markup, parse_mode='Markdown')

    # get ref total referrals
    total = helper.add_ref(u_id, ref) if ref else ''

    # Notify ref that a new user joined
    context.bot.send_message(ref, flow.newRef % total, parse_mode='Markdown') if total else 'pass'
    helper.update_step(u_id, steps.STARTED)

def join(update: Update, context: CallbackContext) -> None:
    u_id:str = update.message.chat.id
    step = helper.fetch_step(u_id)
    if step is None:
        start(update, context)
    elif step is steps.STARTED:
        step = helper.update_step(u_id, steps.JOINING)

    keyboard = [
        ['Registration']
    ]

    # fill placeholders
    m_joining = flow.joining % (_secrets.GROUP.split('@')[-1], _secrets.CHANNEL.split(
        '@')[-1], _secrets.TWITTER_HANDLE, _secrets.FACEBOOK_HANDLE, _secrets.PRO_CHANNEL.split('@')[-1], _secrets.PRO_TWITTER)

    if step == steps.JOINING:
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_joining, reply_markup=reply_markup, parse_mode="Markdown")
        helper.update_step(u_id, steps.REGISTER)

    elif step == steps.REGISTER:
        register(update, context)

    elif step == steps.BEP20:
        bep(update, context)

    elif step == steps.TWITTER:
        twitter(update, context)

    elif step == steps.COMPLETED:
        end_keyboard: list = [
            ['My Balance', 'Information']
        ]
        reply_markup = ReplyKeyboardMarkup(end_keyboard, resize_keyboard=True)
        update.message.reply_text(
            flow.end, reply_markup=reply_markup, parse_mode="Markdown")

def register(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.fetch_step(u_id)
    if step != steps.REGISTER:
        join(update, context)
        return
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=_secrets.GROUP, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT or member.status != ChatMember.KICKED:
            pass
        else:
            raise Exception('Join Group')
    except:
        keyboard = [
            ['Registration'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(flow.forceReg, reply_markup=reply_markup, parse_mode="Markdown")
        return
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=_secrets.CHANNEL, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT or member.status != ChatMember.KICKED:
            pass
        else:
            raise Exception('Join Channel')
    except:
        try:
            # make sure exception wasn't due to bot not being an admin of the channel
            context.bot.get_chat_administrators(chat_id=_secrets.CHANNEL)

            keyboard = [
                ['Registration'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            update.message.reply_text(
                flow.forceReg, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            pass
        
    keyboard = [
        ['Main Menu']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    helper.update_step(u_id, steps.BEP20)
    update.message.reply_text(flow.bep20, reply_markup=reply_markup)

def bep(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.fetch_step(u_id)
    if step != steps.BEP20:
        join(update, context)
        return

    keyboard = [
        ['Main Menu'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    helper.update_step(u_id, steps.TWITTER)
    update.message.reply_text(flow.twitter, reply_markup=reply_markup)

def twitter(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.fetch_step(u_id)
    if step != steps.TWITTER:
        join(update, context)
        return

    keyboard = [
        ['My Balance', 'Information']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    helper.update_step(u_id, steps.COMPLETED)
    update.message.reply_text(flow.end, reply_markup=reply_markup)

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
