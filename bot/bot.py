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
    step = helper.get_user_step(u_id)

    if step == None:
        helper.update_user_step(u_id, steps.STARTED)
    if step == 'COMPLETED':
        join(update, context)

    # Get referral from start 
    ref:str = helper.extract_referral(update.message.text)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    m_welcome:str = flow.welcome % name 

    m_welcome = m_welcome + '\n\nYou were referred by user with id `%s`' % ref if ref else m_welcome + ''
    
    # Reply user
    update.message.reply_text(m_welcome, reply_markup=reply_markup, parse_mode='Markdown')

    # add new ref and get ref total referrals
    total = helper.update_user_refs(u_id, ref) if ref else ''

    # Notify ref that a new user joined
    context.bot.send_message(ref, flow.newRef % total, parse_mode='Markdown') if total else 'pass'

def join(update: Update, context: CallbackContext) -> None:
    u_id:str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step == None:
        start(update, context)
    elif step == steps.STARTED:
        step = helper.update_user_step(u_id, steps.JOINING)

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
        helper.update_user_step(u_id, steps.REGISTER)

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
        m_end = flow.end % u_id
        reply_markup = ReplyKeyboardMarkup(end_keyboard, resize_keyboard=True)
        update.message.reply_text(
            m_end, reply_markup=reply_markup, parse_mode="Markdown")

def register(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)

    m_reply = flow.forceReg % (_secrets.GROUP.split('@')[-1], _secrets.CHANNEL.split('@')[-1])
    if step != steps.REGISTER:
        join(update, context)
        return
    try:
        member:ChatMember = context.bot.get_chat_member(chat_id=_secrets.GROUP, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT and member.status != ChatMember.KICKED:
            tg_grp = helper.get_user_tg_group(u_id)
            if tg_grp != 'joined':
                helper.update_user_tg_group(u_id, 'joined')
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
        member:ChatMember = context.bot.get_chat_member(chat_id=_secrets.CHANNEL, user_id=update.message.chat.id)
        if member.status != ChatMember.LEFT and member.status != ChatMember.KICKED:
            tg_chl = helper.get_user_tg_channel(u_id)
            if tg_chl != 'joined':
                helper.update_user_tg_channel(u_id, 'joined')
            else:
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
                m_reply, reply_markup=reply_markup, parse_mode="Markdown")
            return
        except:
            pass

    helper.update_user_step(u_id, steps.BEP20)
    update.message.reply_text(flow.bep20, parse_mode='Markdown')

def bep(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step != steps.BEP20:
        join(update, context)
        return

    helper.update_user_step(u_id, steps.TWITTER)
    helper.update_user_bep20(u_id, update.message.text)
    update.message.reply_text(
        flow.twitter, parse_mode='Markdown')

def twitter(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step != steps.TWITTER:
        join(update, context)
        return

    keyboard = [
        ['My Balance', 'Information']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    helper.update_user_step(u_id, steps.COMPLETED)
    helper.update_user_twitter(u_id, update.message.text)
    m_end = flow.end % u_id
    update.message.reply_text(
        m_end, reply_markup=reply_markup, parse_mode='Markdown')

def info(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step != steps.COMPLETED:
        join(update, context)
        return
    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        flow.info, reply_markup=reply_markup, parse_mode='Markdown')

def balance(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step != steps.COMPLETED:
        join(update, context)
        return

    user = helper.get_user(u_id)
    count:int = 0
    try:
        count = int(user['refCount'])
    except KeyError:
        count = 0

    keyboard = [
        ['My Balance', 'Information'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    m_balance = flow.balance % (count, int(u_id))
    update.message.reply_text(
        m_balance, reply_markup=reply_markup, parse_mode='Markdown')

def message(update: Update, context:CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step == steps.COMPLETED:
        keyboard = [
            ['My Balance', 'Information'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        wrong_command = "Sorry, wrong command\n\n"
        m_reply = flow.info
        update.message.reply_text(
            wrong_command + m_reply, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        if step == steps.BEP20:
            update.message.reply_text(
                flow.wrong_bep20, parse_mode='Markdown')

        elif step == steps.TWITTER:
            update.message.reply_text(
                flow.wrong_twitter, parse_mode='Markdown')
        else:
            join(update, context)

def change(update: Update, context: CallbackContext) -> None:
    u_id: str = update.message.chat.id
    step = helper.get_user_step(u_id)
    if step not in [steps.STARTED, steps.JOINING, steps.REGISTER]:
        helper.update_user_step(u_id, steps.BEP20)
        update.message.reply_text(flow.bep20, parse_mode='Markdown')
    else:
        join(update, context)

start_handler = CommandHandler('start', start)
change_profile = CommandHandler('changeprofile', change)
join_handler = MessageHandler(Filters.regex("^Join Airdrop$"), join)
register_handler = MessageHandler(Filters.regex("^Registration$"), register)
info_handler = MessageHandler(Filters.regex("^Infomation$"), info)
balance_handler = MessageHandler(Filters.regex("^My Balance$"), balance)
bep_handler = MessageHandler(Filters.regex("^0x[a-fA-F0-9]{40}$"), bep)
twitter_handler = MessageHandler(Filters.regex(
    "^(https:// | http://)?(www\.)?twitter.com/.*"), twitter)
message_handler = MessageHandler(Filters.text, message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(change_profile)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(bep_handler)
dispatcher.add_handler(twitter_handler)
dispatcher.add_handler(message_handler)

updater.start_polling()
