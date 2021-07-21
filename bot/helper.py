from requests import put, get
from _secrets import API_HOST

def extract_referral(message:str) -> str:
    ref = message.split()
    r_v = ref[1] if len(ref) > 1 else ""
    return r_v

def get_user_refs(user_id):
    data = get('%s/%s/refs' % (API_HOST, user_id)).json()
    print(data)
    return data

def update_user_refs(user_id: str, ref_id: str):
    if user_id == ref_id:
        raise Exception('You can\'t refer yourself')

    referredBy = get('%s/%s/referredBy' % (API_HOST, user_id)).json()

    if referredBy == None:
        referredBy_Exits = get('%s/%s' % (API_HOST, ref_id)).json()
        if referredBy_Exits:
            put('%s/%s/referredBy' % (API_HOST, user_id), data={"referredBy":ref_id}).json()
            print('Updated user referral')
            refsCount = put('%s/%s/refs' % (API_HOST, ref_id), data={"ref":user_id}).json()
            return refsCount
        else:
            print('Invalid referral')
            return None
    else:
        print('User is already referred')
        return None

def get_user(user_id: str):
    user: dict = get('%s/%s' % (API_HOST, user_id)).json()
    return user

def get_user_step(user_id):
    step = get('%s/%s/step' % (API_HOST, user_id)).json()
    return step

def update_user_step(user_id, _step):
    step = put('%s/%s/step' % (API_HOST, user_id), data={"step":_step}).json()
    return step

def get_user_tg_group(user_id):
    tg_group = get('%s/%s/tg_group' % (API_HOST, user_id)).json()
    return tg_group

def update_user_tg_group(user_id, _tg_group):
    tg_group = put('%s/%s/tg_group' % (API_HOST, user_id),
               data={"tg_group": _tg_group}).json()
    return tg_group

def get_user_tg_channel(user_id):
    tg_channel = get('%s/%s/tg_channel' % (API_HOST, user_id)).json()
    return tg_channel

def update_user_tg_channel(user_id, _tg_channel):
    tg_channel = put('%s/%s/tg_channel' % (API_HOST, user_id),
               data={"tg_channel": _tg_channel}).json()
    return tg_channel

def get_user_bep20(user_id):
    bep20 = get('%s/%s/bep20' % (API_HOST, user_id)).json()
    return bep20

def update_user_bep20(user_id, _bep20):
    bep20 = put('%s/%s/bep20' % (API_HOST, user_id),
               data={"bep20": _bep20}).json()
    return bep20

def get_user_twitter(user_id):
    twitter = get('%s/%s/twitter' % (API_HOST, user_id)).json()
    return twitter

def update_user_twitter(user_id, _twitter):
    twitter = put('%s/%s/twitter' % (API_HOST, user_id),
               data={"twitter": _twitter}).json()
    return twitter
