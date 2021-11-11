from telegram import ReplyKeyboardMarkup, Update
from telegram.chatmember import ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from _secrets import BOT_TOKEN, GROUP, CHANNEL, TWITTER_HANDLE, FACEBOOK_HANDLE, PRO_CHANNEL, PRO_TWITTER

from flow import welcome, newRef, captcha, captcha_fail, captcha_success, joining, end, info, wrong_twitter, twitter, wrong_bep20, bep20

from helper import get_user_step, update_user_step, update_user_refs, extract_referral
from steps import STARTED, JOINING, REGISTER, CAPTCHA, BEP20, TWITTER, COMPLETED

updater = Updater(token=BOT_TOKEN, use_context=True)
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
    step = get_user_step(u_id)

    if step == None:
        update_user_step(u_id, CAPTCHA)
    if step == 'COMPLETED':
        join(update, context)

    # Get referral from start 
    ref:str = extract_referral(update.message.text)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    m_welcome:str = welcome % name 

    ref_step = get_user_step(ref)

    if ref_step == COMPLETED:
        m_welcome = m_welcome + '\n\nYou were referred by user with id `%s`' % ref

        # add new ref and get ref total referrals
        total = update_user_refs(u_id, ref) if ref else ''
    
        # Notify ref that a new user joined
        context.bot.send_message(ref, newRef % total, parse_mode='Markdown') if total else 'pass'
    
    # Reply user
    update.message.reply_text(m_welcome, reply_markup=reply_markup, parse_mode='Markdown')

def join(update: Update, context: CallbackContext) -> None:
    u_id:str = update.message.chat.id
    step = get_user_step(u_id)
    if step == None:
        start(update, context)
    elif step == CAPTCHA:
        isHuman(update, context)
    elif step == STARTED:
        step = update_user_step(u_id, JOINING)

    keyboard = [
        ['Registration']
    ]

    # fill placeholders
    m_joining = joining % (GROUP.split('@')[-1], CHANNEL.split(
        '@')[-1], TWITTER_HANDLE, FACEBOOK_HANDLE, PRO_CHANNEL.split('@')[-1], PRO_TWITTER)

    if step == JOINING:
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_joining, reply_markup=reply_markup, parse_mode="Markdown")
        update_user_step(u_id, REGISTER)

    elif step == REGISTER:
        register(update, context)

    elif step == BEP20:
        bep(update, context)

    elif step == TWITTER:
        tweeter(update, context)

    elif step == COMPLETED:
        end_keyboard: list = [
            ['My Balance', 'Information']
        ]
        m_end = end % u_id
        reply_markup = ReplyKeyboardMarkup(end_keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_end, reply_markup=reply_markup, parse_mode="Markdown")

def register(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)

    m_reply = forceReg % (GROUP.split('@')[-1], CHANNEL.split('@')[-1])
    if step != REGISTER:
        join(update, context)
        return
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=GROUP, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT and member.status != ChatMember.KICKED:
            tg_grp = get_user_tg_group(u_id)
            if tg_grp != 'joined':
                update_user_tg_group(u_id, 'joined')
            else:
                pass
        else:
            raise Exception('Join Group')
    except:
        keyboard = [
            ['Registration'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(m_reply, reply_markup=reply_markup, parse_mode="Markdown")
        return
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=CHANNEL, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT and member.status != ChatMember.KICKED:
            tg_chl = get_user_tg_channel(u_id)
            if tg_chl != 'joined':
                update_user_tg_channel(u_id, 'joined')
            else:
                pass
        else:
            raise Exception('Join Channel')
    except:
        try:
            # make sure exception wasn't due to bot not being an admin of the channel
            context.bot.get_chat_administrators(chat_id=CHANNEL)
            keyboard = [
                ['Registration'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            update.message.reply_text(
                m_reply, reply_markup=reply_markup, parse_mode="Markdown")
            return
        except:
            pass

    update_user_step(u_id, BEP20)
    update.message.reply_text(bep20, parse_mode='Markdown')

def bep(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != BEP20:
        join(update, context)
        return

    update_user_step(u_id, TWITTER)
    update_user_bep20(u_id, update.message.text)
    update.message.reply_text(
        twitter, parse_mode='Markdown')

def tweeter(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != TWITTER:
        join(update, context)
        return

    keyboard = [
        ['My Balance', 'Information']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update_user_step(u_id, COMPLETED)
    update_user_twitter(u_id, update.message.text)
    m_end = end % u_id
    update.message.reply_text(
        m_end, reply_markup=reply_markup, parse_mode='Markdown')

def information(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != COMPLETED:
        join(update, context)
        return
    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        info, reply_markup=reply_markup, parse_mode='Markdown')

def balance(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != COMPLETED:
        join(update, context)
        return

    user = get_user(u_id)
    count:int = 0
    try:
        count = int(user['ref_count'])
    except KeyError:
        pass

    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    m_balance = balance % (count, int(u_id))
    update.message.reply_text(
        m_balance, reply_markup=reply_markup, parse_mode='Markdown')

def message(update: Update, context:CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step == COMPLETED:
        keyboard = [
            ['My Balance', 'Information'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        wrong_command = "Sorry, wrong command\n\n"
        m_reply = info
        update.message.reply_text(
            wrong_command + m_reply, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        if step == BEP20:
            update.message.reply_text(
                wrong_bep20, parse_mode='Markdown')

        elif step == TWITTER:
            update.message.reply_text(
                wrong_twitter, parse_mode='Markdown')
        else:
            join(update, context)

def change(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step not in [STARTED, JOINING, REGISTER]:
        update_user_step(u_id, BEP20)
        update.message.reply_text(bep20, parse_mode='Markdown')
    else:
        join(update, context)

def isHuman(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    update_user_step(u_id, STARTED)
    join(update, context)
    
start_handler = CommandHandler('start', start)
change_profile = CommandHandler('changeprofile', change)
join_handler = MessageHandler(Filters.regex("^Join Airdrop$"), join)
register_handler = MessageHandler(Filters.regex("^Registration$"), register)
info_handler = MessageHandler(Filters.regex("^Infomation$"), information)
balance_handler = MessageHandler(Filters.regex("^My Balance$"), balance)
bep_handler = MessageHandler(Filters.regex("^0x[a-fA-F0-9]{40}$"), bep)
twitter_handler = MessageHandler(Filters.regex(
    "^(https:// | http://)?(www\.)?twitter.com/.*"), tweeter)
message_handler = MessageHandler(Filters.text, message)
captcha_handler = MessageHandler(Filters.text, isHuman)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(change_profile)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(captcha_handler)
dispatcher.add_handler(bep_handler)
dispatcher.add_handler(twitter_handler)
dispatcher.add_handler(message_handler)

updater.start_polling()
