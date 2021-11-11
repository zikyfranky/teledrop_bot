from firebase_admin import db

def get_user_reference(user_id):
    user = db.reference('users/%s' % user_id)
    return user

def get_user(user_id):
    user = get_user_reference(user_id).get()
    return user

def get_user_referral(user_id):
    referral = get_user_reference(user_id).child('referredBy').get()
    return referral

def update_user_referral(user_id, ref_id):
    get_user_reference(user_id).child('referredBy').set(ref_id)
    return get_user_referral(user_id)

def get_user_refs(user_id):
    refs = get_user_reference(user_id).child('refs').get()
    return refs

def update_user_refs(user_id, ref):
    get_user_reference(user_id).child('refs').push(ref)
    count = len(get_user_refs(user_id).keys())
    get_user_reference(user_id).child('ref_count').set(count)
    return count

def get_user_ref_count(user_id):
    ref_count = get_user_reference(user_id).child('ref_count').get()
    return int(ref_count)

def get_user_bep20(user_id):
    bep20 = get_user_reference(user_id).child('bep20').get()
    return bep20

def update_user_bep20(user_id, _bep20):
    get_user_reference(user_id).child('bep20').set(_bep20)
    return get_user_bep20(user_id)

def get_user_twitter_username(user_id):
    twitter = get_user_reference(user_id).child('twitter-username').get()
    return twitter

def update_user_twitter_username(user_id, _twitter):
    get_user_reference(user_id).child('twitter-username').set(_twitter)
    return get_user_twitter_username(user_id)

def get_user_twitter_retweet_link(user_id):
    twitter = get_user_reference(user_id).child('twitter-retweet-link').get()
    return twitter

def update_user_twitter_retweet_link(user_id, _twitter):
    get_user_reference(user_id).child('twitter-retweet-link').set(_twitter)
    return get_user_twitter_retweet_link(user_id)

def get_user_step(user_id):
    step = get_user_reference(user_id).child('step').get()
    return step

def update_user_step(user_id, _step):
    get_user_reference(user_id).child('step').set(_step)
    return get_user_step(user_id)

def get_user_tg_group(user_id):
    tg_group = get_user_reference(user_id).child('tg_group').get()
    return tg_group

def update_user_tg_group(user_id, _tg_group):
    get_user_reference(user_id).child('tg_group').set(_tg_group)
    return get_user_tg_group(user_id)

def get_user_tg_channel(user_id):
    tg_channel = get_user_reference(user_id).child('tg_channel').get()
    return tg_channel

def update_user_tg_channel(user_id, _tg_channel):
    get_user_reference(user_id).child('tg_channel').set(_tg_channel)
    return get_user_tg_channel(user_id)
