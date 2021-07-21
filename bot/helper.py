from requests import put, get
from _secrets import API_HOST

def extract_referral(message:str) -> str:
    ref = message.split()
    r_v = ref[1] if len(ref) > 1 else ""
    return r_v

def increment_referee_count(user_id: str, ref_id: str, ref_obj) -> int:
    refs: list = ref_obj['refs'].val()
    refCount: int = ref_obj['refCount']
    refCount +=1
    refs.append(user_id)
    put(API_HOST + '/' + ref_id, data={'refs': refs, 'refCount':refCount}).json()
    return refCount

def add_ref(user_id:str, ref_id:str):
    if user_id == ref_id:
        raise Exception('You can\'t refer yourself')

    user = get('%s/%s' % (API_HOST, user_id)).json()
    user_exists = user.get('status_code') == 200

    if user_exists:
        user_ref = user.get('data')['ref']
        if not user_ref:
            ref = get('%s/%s' % (API_HOST, ref_id)).json()
            ref_exists = ref.get('status_code') == 200
            if ref_exists:
                res = put('%s/%s' % (API_HOST, user_id), data={'ref': ref_id}).json()
                if res.get('status_code') == 200:
                    print('Updated user referral')
                    return increment_referee_count(user_id, ref_id, ref.get('data'))
                else:
                    print('Error saving referral')
            else:
                print('Invalid referral')
        else:
            print('User is already referred')


def fetch_user(user_id: str):
    user: dict = get('%s/%s' % (API_HOST, user_id)).json()
    user_exists = user.get('status_code') == 200

    if user_exists:
        return user.get('data')
    else:
        return None

def update_user(user_id: str, data):
    res = put('%s/%s' % (API_HOST, user_id), data=data).json()
    if res.get('status_code') == 200:
        print('Updated User')
        return True
    else:
        print('Error saving step')
        return False

def update_step(user_id:str, step:str):
    res = update_user(user_id, data={'step': step}).json()
    return step if res else None

def fetch_step(user_id:str):
    user:dict = fetch_user(user_id)
    if user is not None:
        return user['step']
    else: 
        return None
