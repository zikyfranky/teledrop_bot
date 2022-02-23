from flask import Flask
from flask import request
from flask import Response
from urllib.parse import urlencode
import requests

import json

from os import environ
import re
from flow import welcome, ENDED, newRef, captcha, captcha_fail, forceReg, captcha_success, joining, end, info, wrong_twitter_username, twitter_username_text, twitter_retweet_link_text, wrong_bep20, bep20, balance_text, success

from helper import get_isCompleted, get_user, get_user_step, get_user_twitter_retweet_link, get_user_twitter_username, update_isCompleted, update_user_step, update_user_refs, extract_referral, get_user_tg_group, update_user_tg_group, get_user_tg_channel, update_user_tg_channel, update_user_bep20, update_user_twitter_link, update_user_twitter_username

from steps import STARTED, JOINING, REGISTER, CAPTCHA, BEP20, TWITTER_USERNAME, TWITTER_RETWEET_LINK, COMPLETED

from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = environ.get('BOT_TOKEN')
GROUP = environ.get('GROUP')
CHANNEL = environ.get('CHANNEL')
TWITTER_HANDLE = environ.get('TWITTER_HANDLE')
ME = environ.get('ME')
PORT = int(environ.get('PORT', '8443'))


teleAPI = "https://api.telegram.org/bot"+BOT_TOKEN

app = Flask(__name__)

# Airdrop has ended
is_ended = True  # @TODO fetch this from DB or externally


def reply_markup(keyboard, otk=False):
    """
    Serialize keyboard data to JSON.
    Arguments:
        keyboard: the keyboard to send
        otk: Disappears on click
    Returns:
        The JSON object
    """
    return json.dumps({'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': otk})


def call_api_method(method='getMe', data=None):
    """
    Make a telegram API call without receiving the response
    Arguments:
        method: the telegram method to call
        data: some data to pass onto the api call
    Returns:
        A Response object with status 200
    """

    data = urlencode(data) if data else data
    url = '{}/{}?{}'.format(teleAPI, method, data)
    requests.get(url)
    return Response('Ok', status=200)


def call_api_method_get(method='getMe', data=None):
    """
    Make a telegram API call without receiving the response
    Arguments:
        method: the telegram method to call
        data: some data to pass onto the api call
    Returns:
        The return data of the api
    """
    data = urlencode(data) if data else data
    url = '{}/{}?{}'.format(teleAPI, method, data)
    return requests.get(url)


def has_ended(u_id):
    """
    Send message to users if airdrop has ended

    Arguments:
        u_id: id of the caller
    """
    keyboard: list = [
        ['My Balance']
    ]

    data = {'text': ENDED, 'chat_id':  u_id, 'parse_mode': 'Markdown',
            'reply_markup': reply_markup(keyboard)}

    # Reply users
    return call_api_method('sendMessage', data)


def start(update) -> Response:
    keyboard: list = [
        ['Join Airdrop'],
        ['My Balance']
    ]

    # get name and ID, if no name, use id
    name: str = update['message']['chat']['first_name']
    u_id: str = update['message']['chat']['id']
    name = name if name else u_id
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)

    if step == None:
        update_user_step(u_id, STARTED)
        text = update['message']['text']

        # Get referral from start
        ref: str = extract_referral(text)
        m_welcome: str = welcome % name

        # Add to ref count only if ref has completed all tasks
        ref_step = get_isCompleted(ref) if ref else False
        if ref_step == "True":
            m_welcome = m_welcome + '\nYou were referred by user with id %s' % ref

            # add new ref and get ref total referrals
            total = update_user_refs(u_id, ref)

            data = {'text': newRef % total,
                    'chat_id': ref, 'parse_mode': 'HTML'}

            # Notify ref that a new user joined
            call_api_method('sendMessage', data)

        # Welcome user
        data = {'text': m_welcome, 'chat_id':  update['message']['chat']
                ['id'], 'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}

        return call_api_method('sendMessage', data)
    else:
        return join(update)


def join(update) -> Response:
    """
    Directs all calls to the right function
    Arguments:
        update: chat object injected by telegram
    Returns:
        Response type
    """
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step == None:
        return start(update)

    # @TODO Add Captcha in new version
    # elif step == CAPTCHA:
        # Captcha logic
    elif step == STARTED:
        step = update_user_step(u_id, JOINING)
        return join(update)

    keyboard = [
        ['Register']
    ]

    # fill placeholders
    m_joining = joining % (GROUP.split('@')[-1], CHANNEL.split(
        '@')[-1], TWITTER_HANDLE)

    if step == JOINING:
        data = {'text': m_joining, 'chat_id': u_id,
                'reply_markup': reply_markup(keyboard), 'parse_mode': 'HTML'}

        update_user_step(u_id, REGISTER)

        return call_api_method('sendMessage', data)

    elif step == REGISTER:
        return register(update)

    elif step == BEP20:
        return bep(update)

    elif step == TWITTER_USERNAME:
        return twitter_username(update)

    elif step == TWITTER_RETWEET_LINK:
        return twitter_retweet_link(update)

    elif step == COMPLETED:
        end_keyboard: list = [
            ['My Balance', 'Information']
        ]

        m_end = end % (ME, u_id)
        data = {'text': m_end, 'chat_id': update['message']['chat']['id'], 'reply_markup': reply_markup(
            end_keyboard), 'parse_mode': 'HTML'}

        return call_api_method('sendMessage', data)
    else:
        return Response('OK', status=200)


def register(update) -> Response:
    """
    Registration Logic
    Arguments:
        update: chat object injected by telegram
    Returns:
        Response type
    """
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)

    m_reply = forceReg % (GROUP.split('@')[-1], CHANNEL.split('@')[-1])
    if step != REGISTER:
        return join(update)
    try:
        data = {"chat_id": GROUP, "user_id": u_id}
        member = call_api_method_get('getChatMember', data)
        if member['ok']:
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
            data = {"chat_id": GROUP}
            # make sure exception wasn't due to bot not being an admin of the channel
            res = call_api_method_get('getChatAdministrators', data)
            if not res['ok']:
                raise Exception('Failed')  # Bot isn't an admin

            keyboard = [
                ['Register'],
            ]

            data = {'text': m_reply, 'chat_id':  u_id,
                    'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}

            # Reply user
            return call_api_method('sendMessage', data)
        except:
            pass
    try:
        data = {"chat_id": CHANNEL, "user_id": u_id}
        member = call_api_method_get('getChatMember', data)
        if member['ok']:
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
            data = {"chat_id": CHANNEL}
            # make sure exception wasn't due to bot not being an admin of the channel
            res = call_api_method_get('getChatAdministrators', data)
            if not res['ok']:
                raise Exception('Failed')

            keyboard = [
                ['Register'],
            ]

            data = {'text': m_reply, 'chat_id':  u_id,
                    'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}

            # Reply users
            return call_api_method('sendMessage', data)
        except:
            pass

    data = {'text': bep20, 'chat_id':  u_id, 'parse_mode': 'HTML'}
    update_user_step(u_id, BEP20)

    # Reply user
    return call_api_method('sendMessage', data)


def bep(update) -> Response:
    """
    Handle Wallet Input
    Arguments:
        update: chat object injected by telegram
    Returns:
        Response type
    """
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step != BEP20:
        return join(update)

    text = update['message']['text']
    # Should match EVM address type
    isMatch = re.match(r'^0x[a-fA-F0-9]{40}$', text)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    if isMatch == None:
        data = {'text': wrong_bep20, 'chat_id':  u_id, 'parse_mode': 'HTML'}

        return call_api_method('sendMessage', data)
    else:
        update_user_bep20(u_id, text)
        if(get_user_twitter_username(u_id) == None):
            # Continue the flow
            update_user_step(u_id, TWITTER_USERNAME)
            data = {'text': twitter_username_text,
                    'chat_id':  u_id, 'parse_mode': 'HTML'}
            return call_api_method('sendMessage', data)
        else:
            # Call was a change, notify user of the updated address
            update_user_step(u_id, COMPLETED)

            data = {'text': success % 'BEP20', 'chat_id':  u_id,
                    'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}
            return call_api_method('sendMessage', data)


def twitter_username(update) -> Response:
    """
    Twitter Username
    Arguments:
        update: chat object injected by telegram
    Returns:
        Response type
    """
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step != TWITTER_USERNAME:
        return join(update)

    text = update['message']['text']
    isMatch = re.match(r'^@.*$', text)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    if isMatch == None:
        data = {'text': wrong_twitter_username, 'chat_id':  u_id,
                'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard, True)}
        return call_api_method('sendMessage', data)
    else:
        update_user_twitter_username(u_id, text)
        if(get_user_twitter_retweet_link(u_id) == None):
            update_user_step(u_id, TWITTER_RETWEET_LINK)
            data = {'text': twitter_retweet_link_text,
                    'chat_id':  u_id, 'parse_mode': 'HTML'}
            return call_api_method('sendMessage', data)
        else:
            update_user_step(u_id, COMPLETED)

            data = {'text': success % 'USERNAME', 'chat_id':  u_id,
                    'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}
            return call_api_method('sendMessage', data)


def twitter_retweet_link(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    if step != TWITTER_RETWEET_LINK:
        return join(update)

    text = update['message']['text']
    m_end = end % (ME, u_id)

    update_user_twitter_link(u_id, text)  # @TODO Verify link is valid
    update_user_step(u_id, COMPLETED)
    update_isCompleted(u_id)

    data = {'text': success % 'RETWEET LINK',
            'chat_id':  u_id, 'parse_mode': 'Markdown'}
    call_api_method('sendMessage', data)

    data = {'text': m_end, 'chat_id':  u_id, 'parse_mode': 'HTML',
            'reply_markup': reply_markup(keyboard)}
    return call_api_method('sendMessage', data)


def information(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if step != COMPLETED:
        return join(update)

    keyboard = [
        ['My Balance', 'Information'],
    ]

    data = {'text': info % (ME, u_id), 'chat_id':  u_id,
            'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}
    return call_api_method('sendMessage', data)


def balance(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if step != COMPLETED:
        return join(update)

    user = get_user(u_id)
    count: int = 0
    try:
        count = int(user['ref_count'])
    except KeyError:
        pass

    keyboard = [
        ['My Balance', 'Information']
    ]
    m_balance = balance_text % (5000*count, count)  # , ME, int(u_id))

    data = {'text': m_balance, 'chat_id':  u_id,
            'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}
    return call_api_method('sendMessage', data)


def message(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step == COMPLETED:
        keyboard = [
            ['My Balance'],
        ]

        wrong_command = "Airdrop Has Ended\n\n" if is_ended else "You have completed this airdrop\n\n"
        m_reply = info % (wrong_command)

        data = {'text': m_reply, 'chat_id':  u_id,
                'parse_mode': 'HTML', 'reply_markup': reply_markup(keyboard)}
        return call_api_method('sendMessage', data)
    # elif step == CAPTCHA:
    #     CAPTCHA HANDLER
    else:
        return start(update)


def update_username(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step == COMPLETED:
        update_user_step(u_id, TWITTER_USERNAME)
        data = {'text': twitter_username_text,
                'chat_id':  u_id, 'parse_mode': 'HTML'}
        return call_api_method('sendMessage', data)
    else:
        return join(update)


def update_link(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step == COMPLETED:
        update_user_step(u_id, TWITTER_RETWEET_LINK)
        data = {'text': twitter_retweet_link_text,
                'chat_id':  u_id, 'parse_mode': 'HTML'}
        return call_api_method('sendMessage', data)
    else:
        return join(update)


def update_bep20(update) -> Response:
    u_id: str = update['message']['chat']['id']
    step = get_user_step(u_id)

    if is_ended:
        return has_ended(u_id)
    if step == COMPLETED:
        update_user_step(u_id, BEP20)
        data = {'text': bep20, 'chat_id':  u_id, 'parse_mode': 'HTML'}
        return call_api_method('sendMessage', data)
    else:
        return join(update)


@app.route('/', methods=['GET'])
def index():
    return '<h1>RUNNING</h1>'


@app.route('/'+BOT_TOKEN, methods=['POST'])
def hook():
    """Webhook URL should be based on @BOT_TOKEN as this is hard to guess"""

    update = request.get_json()
    text = ''
    try:
        text = update['message']['text']
    except KeyError:
        return Response('Ok', status=200)

    # Get All Commands
    if text.startswith('/start'):
        return start(update)
    elif text.startswith('/update_bep20'):
        return update_bep20(update)
    elif text.startswith('/update_username'):
        return update_username(update)
    elif text.startswith('/update_link'):
        return update_link(update)
    else:
        isJoin = re.match(r'^Join Airdrop$', text)
        isReg = re.match(r'^Register$', text)
        isInfo = re.match(r'^Information$', text)
        isBal = re.match(r'^My Balance$', text)

        if isJoin:
            return join(update)
        elif isReg:
            return register(update)
        elif isInfo:
            return information(update)
        if isBal:
            return balance(update)
        else:
            return message(update)


if __name__ == '__main__':
    app.run(debug=False)
