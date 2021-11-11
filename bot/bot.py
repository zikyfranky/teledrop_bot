import re
from telegram import ReplyKeyboardMarkup, Update
from telegram.chatmember import ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from _secrets import BOT_TOKEN, GROUP, CHANNEL, TWITTER_HANDLE, ME

from flow import welcome, newRef, captcha, captcha_fail, forceReg, captcha_success, joining, end, info, wrong_twitter_username, twitter_username_text, twitter_retweet_link_text, wrong_twitter_retweet_link, wrong_bep20, bep20, balance_text

from helper import get_user, get_user_step, update_user_step, update_user_refs, extract_referral, get_user_tg_group,update_user_tg_group,get_user_tg_channel,update_user_tg_channel,update_user_bep20, update_user_twitter_link, update_user_twitter_username

from steps import STARTED, JOINING, REGISTER, CAPTCHA, BEP20, TWITTER_USERNAME, TWITTER_RETWEET_LINK, COMPLETED

from captcha import captcha_gen


# Logic starts here
CAPTCHA_EQ:str = ''
CAPTCHA_SOL:int = 0

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext) -> None:
    keyboard:list = [
        ['Verify You Are Human']
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

def verify(update: Update, context: CallbackContext) -> None:
    join(update, context)

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
        '@')[-1], TWITTER_HANDLE)

    if step == JOINING:
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_joining, reply_markup=reply_markup, parse_mode="Markdown")
        update_user_step(u_id, REGISTER)

    elif step == REGISTER:
        register(update, context)

    elif step == BEP20:
        bep(update, context)

    elif step == TWITTER_USERNAME:
        twitter_username(update, context)

    elif step == TWITTER_RETWEET_LINK:
        twitter_retweet_link(update, context)

    elif step == COMPLETED:
        end_keyboard: list = [
            ['My Balance', 'Information']
        ]
        m_end = end % ME, u_id
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
            # User has left the group or isn't a member, trigger except block
            raise Exception('Join Group')
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
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=CHANNEL, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT and member.status != ChatMember.KICKED:
            tg_chl = get_user_tg_channel(u_id)
            if tg_chl != 'joined':
                update_user_tg_channel(u_id, 'joined')
            else:
                pass
        else:
            # Trigget except block
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

    text = update.message.text
    isMatch = re.match(r'^0x[a-fA-F0-9]{40}$', text)

    if isMatch == None:
        update.message.reply_text(
            wrong_bep20, parse_mode='Markdown')
        return
    else:
        update_user_bep20(u_id, text)
        update_user_step(u_id, TWITTER_USERNAME)
        update.message.reply_text(
            twitter_username_text%ME, parse_mode='Markdown')

def twitter_username(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != TWITTER_USERNAME:
        join(update, context)
        return

    text = update.message.text
    isMatch = re.match(r'^@[a-fA-F0-9].*$', text)

    if isMatch == None:
        update.message.reply_text(
            wrong_twitter_username, parse_mode='Markdown')
        return
    else:
        update_user_step(u_id, TWITTER_RETWEET_LINK)
        update_user_twitter_username(u_id, text)
        update.message.reply_text(
            twitter_retweet_link_text, parse_mode='Markdown')

def twitter_retweet_link(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    if step != TWITTER_RETWEET_LINK:
        join(update, context)
        return

    text = update.message.text

    isMatch = re.match(r'^(https:// | http://)?(www\.)?twitter.com/[a-fA-F0-9]/status/.*', text)

    if isMatch == None:
        update.message.reply_text(
            wrong_twitter_retweet_link, parse_mode='Markdown')
        return
    else:
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        m_end = end % u_id

        update_user_twitter_link(u_id, text)
        update_user_step(u_id, COMPLETED)

        update.message.reply_text(
            m_end, reply_markup=reply_markup,parse_mode='Markdown')

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
        info%(ME, u_id), reply_markup=reply_markup, parse_mode='Markdown')

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
    m_balance = balance_text % (ME, count, int(u_id))
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
        wrong_command = "You've Completed The Airdrop\n\n"
        m_reply = wrong_command+info%(ME,u_id)
        update.message.reply_text(
            m_reply, reply_markup=reply_markup, parse_mode='Markdown')
    elif step == CAPTCHA:
        _captchaChecker(update, context)
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

def _captchaSuccess(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    update_user_step(u_id, STARTED)
    update.message.reply_text(
        captcha_success, parse_mode='Markdown')
    join(update, context)

def _captchaFail(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(captcha_fail, parse_mode='Markdown')
    join(update, context)

def _captchaChecker(update: Update, context: CallbackContext) -> None:
    answer = 0
    try:
        answer = int(update.message.text)
        if(answer == CAPTCHA_SOL):
            _captchaSuccess(update, context)
        else:
            _captchaFail(update, context)
    except ValueError:
        _captchaFail(update, context)

def isHuman(update: Update, context: CallbackContext) -> None:
    eq, sol = captcha_gen()

    global CAPTCHA_EQ
    global CAPTCHA_SOL

    CAPTCHA_EQ = eq
    CAPTCHA_SOL = sol

    update.message.reply_text(captcha%CAPTCHA_EQ, parse_mode='Markdown')
    
start_handler = CommandHandler('start', start)
change_profile = CommandHandler('changeprofile', change)
join_handler = MessageHandler(Filters.regex("^Verify You Are Human$"), verify)
register_handler = MessageHandler(Filters.regex("^Registration$"), register)
info_handler = MessageHandler(Filters.regex("^Infomation$"), information)
balance_handler = MessageHandler(Filters.regex("^My Balance$"), balance)
twitter_handler = MessageHandler(Filters.regex(
    "^(https:// | http://)?(www\.)?twitter.com/.*"), twitter_username)
message_handler = MessageHandler(Filters.text, message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(change_profile)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(twitter_handler)
dispatcher.add_handler(message_handler)

updater.start_polling()
