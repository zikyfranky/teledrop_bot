from os import environ
import re
from telegram import ReplyKeyboardMarkup, Update
from telegram.chatmember import ChatMember
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from flow import welcome, ENDED, newRef, captcha, captcha_fail, forceReg, captcha_success, joining, end, info, wrong_twitter_username, twitter_username_text, twitter_retweet_link_text, wrong_bep20, bep20, balance_text, success

from helper import get_isCompleted, get_user, get_user_step, get_user_twitter_retweet_link, get_user_twitter_username, update_isCompleted, update_user_step, update_user_refs, extract_referral, get_user_tg_group, update_user_tg_group, get_user_tg_channel, update_user_tg_channel, update_user_bep20, update_user_twitter_link, update_user_twitter_username

from steps import STARTED, JOINING, REGISTER, CAPTCHA, BEP20, TWITTER_USERNAME, TWITTER_RETWEET_LINK, COMPLETED
from captcha import captcha_gen

from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = environ.get('BOT_TOKEN')
GROUP = environ.get('GROUP')
CHANNEL = environ.get('CHANNEL')
TWITTER_HANDLE = environ.get('TWITTER_HANDLE')
ME = environ.get('ME')
PORT = int(environ.get('PORT', '8443'))

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Airdrop has ended
is_ended = True  # @TODO fetch this from DB or externally


def has_ended(update,):
    """
    Send message to user if airdrop has ended
    """
    keyboard: list = [
        ['My Balance']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        ENDED, parse_mode='Markdown', reply_markup=reply_markup)


def start(update: Update, context: CallbackContext) -> None:
    keyboard: list = [
        ['Join Airdrop'],
        ['My Balance']
    ]

    # get name and ID, if no name, use id
    name: str = update.message.chat.first_name
    u_id: str = update.message.chat.id
    name = name if name else u_id
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(update)

    if step == None:
        update_user_step(u_id, STARTED)
        # Get referral from start
        ref: str = extract_referral(update.message.text)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        m_welcome: str = welcome % name

        ref_step = get_isCompleted(ref) if ref else False

        if ref_step == "True":
            m_welcome = m_welcome + '\nYou were referred by user with id `%s`' % ref

            # add new ref and get ref total referrals
            total = update_user_refs(u_id, ref)

            # Notify ref that a new user joined
            context.bot.send_message(
                ref, newRef % total, parse_mode='Markdown')

        # Welcome user
        update.message.reply_text(
            m_welcome, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        join(update, context)


def join(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if is_ended:
        return has_ended(update)
    if step == None:
        start(update, context)
    # @TODO Add Captcha in new version
    # elif step == CAPTCHA:
        # Captcha logic
    elif step == STARTED:
        step = update_user_step(u_id, JOINING)
        return join(update, context)

    keyboard = [
        ['Register']
    ]

    # fill placeholders
    m_joining = joining % (GROUP.split('@')[-1], CHANNEL.split(
        '@')[-1], TWITTER_HANDLE)

    if step == JOINING:
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update_user_step(u_id, REGISTER)
        update.message.reply_text(
            m_joining, reply_markup=reply_markup, parse_mode="Markdown")

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
        m_end = end % (ME, u_id)
        reply_markup = ReplyKeyboardMarkup(end_keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_end, reply_markup=reply_markup, parse_mode="HTML")


def register(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(update)

    m_reply = forceReg % (GROUP.split('@')[-1], CHANNEL.split('@')[-1])
    if step != REGISTER:
        return join(update, context)
    try:
        member: ChatMember = context.bot.get_chat_member(
            chat_id=GROUP, user_id=update.message.chat.id)
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
                ['Register'],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            update.message.reply_text(
                m_reply, reply_markup=reply_markup, parse_mode="Markdown")
            return
        except:
            pass
    try:
        member: ChatMember = context.bot.get_chat_member(
            chat_id=CHANNEL, user_id=update.message.chat.id)
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
                ['Register'],
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

    if is_ended:
        return has_ended(update)

    if step != BEP20:
        return join(update, context)

    text = update.message.text
    # Should match EVM address type
    isMatch = re.match(r'^0x[a-fA-F0-9]{40}$', text)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if isMatch == None:
        update.message.reply_text(
            wrong_bep20, parse_mode='Markdown')
        return
    else:
        update_user_bep20(u_id, text)
        if(get_user_twitter_username(u_id) == None):
            update_user_step(u_id, TWITTER_USERNAME)
            update.message.reply_text(
                twitter_username_text, parse_mode='HTML')
        else:
            update_user_step(u_id, COMPLETED)
            update.message.reply_text(
                success % 'BEP20', reply_markup=reply_markup, parse_mode='Markdown')


def twitter_username(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if is_ended:
        return has_ended(update)
    if step != TWITTER_USERNAME:
        return join(update, context)

    text = update.message.text
    isMatch = re.match(r'^@.*$', text)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True)

    if isMatch == None:
        update.message.reply_text(
            wrong_twitter_username, parse_mode='Markdown')
        return
    else:
        update_user_twitter_username(u_id, text)
        if(get_user_twitter_retweet_link(u_id) == None):
            update_user_step(u_id, TWITTER_RETWEET_LINK)
            update.message.reply_text(
                twitter_retweet_link_text, parse_mode='Markdown')
        else:
            update_user_step(u_id, COMPLETED)
            update.message.reply_text(
                success % 'USERNAME', reply_markup=reply_markup, parse_mode='Markdown')


def twitter_retweet_link(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    if is_ended:
        return has_ended(update)

    if step != TWITTER_RETWEET_LINK:
        return join(update, context)

    text = update.message.text
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    m_end = end % (ME, u_id)

    update_user_twitter_link(u_id, text)  # @TODO Verify link is valid

    update_user_step(u_id, COMPLETED)
    update_isCompleted(u_id)
    update.message.reply_text(
        success % 'LINK', parse_mode='Markdown')

    update.message.reply_text(
        m_end, reply_markup=reply_markup, parse_mode='HTML')


def information(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)

    if step != COMPLETED:
        return join(update, context)

    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        info % (ME, u_id), reply_markup=reply_markup, parse_mode='HTML')


def balance(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step != COMPLETED:
        return join(update, context)

    user = get_user(u_id)
    count: int = 0
    try:
        count = int(user['ref_count'])
    except KeyError:
        pass

    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    m_balance = balance_text % (5000*count, count, ME, int(u_id))
    update.message.reply_text(
        m_balance, reply_markup=reply_markup, parse_mode='HTML')


def message(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if step == COMPLETED:
        keyboard = [
            ['My Balance', 'Information'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        wrong_command = "You've Completed The Airdrop\n\n"
        m_reply = wrong_command+info % (ME, u_id)
        update.message.reply_text(
            m_reply, reply_markup=reply_markup, parse_mode='HTML')
    # elif step == CAPTCHA:
    #     CAPTCHA HANDLER
    else:
        return start(update, context)


def update_username(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if is_ended:
        return has_ended(update)
    if step == COMPLETED:
        update_user_step(u_id, TWITTER_USERNAME)
        update.message.reply_text(twitter_username_text, parse_mode='HTML')
    else:
        return join(update, context)


def update_link(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if is_ended:
        return has_ended(update)
    if step == COMPLETED:
        update_user_step(u_id, TWITTER_RETWEET_LINK)
        update.message.reply_text(
            twitter_retweet_link_text, parse_mode='Markdown')
    else:
        join(update, context)


def update_bep20(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = get_user_step(u_id)
    if is_ended:
        return has_ended(update)
    if step == COMPLETED:
        update_user_step(u_id, TWITTER_USERNAME)
        update.message.reply_text(twitter_username_text, parse_mode='Markdown')
    else:
        join(update, context)


start_handler = CommandHandler('start', start)
change_bep20 = CommandHandler('update_bep20', update_bep20)
change_username = CommandHandler('update_username', update_username)
change_link = CommandHandler('update_link', update_link)
join_handler = MessageHandler(Filters.regex("^Join Airdrop$"), join)
register_handler = MessageHandler(Filters.regex("^Register$"), register)
info_handler = MessageHandler(Filters.regex("^Information$"), information)
balance_handler = MessageHandler(Filters.regex("^My Balance$"), balance)
message_handler = MessageHandler(Filters.text, message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(change_bep20)
dispatcher.add_handler(change_username)
dispatcher.add_handler(change_link)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(message_handler)

updater.start_polling()
updater.idle()
