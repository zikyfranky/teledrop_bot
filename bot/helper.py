from requests import put, get
from _secrets import API_HOST

def extract_referral(message:str) -> str:
    ref = message.split()
    r_v = ref[1] if len(ref) > 1 else ""
    return r_v


def increment_referee_count(user_id: str, ref_id: str, ref_obj) -> int:
    refs: list = ref_obj.refs.val()
    refCount: int = ref_obj.refCount
    refCount +=1
    refs.append(user_id)
    put(API_HOST + '/' + ref_id, data={'refs': refs, 'refCount':refCount}).json()
    return refCount

def add_ref(user_id:str, ref_id:str):
    if user_id == ref_id:
        raise Exception('You can\'t refer yourself')

    user = get('%s/%s' % (API_HOST, user_id)).json()
    user_exists = user.status_code == 200

    if user_exists:
        user_ref = user.data.ref
        if not user_ref:
            ref = get(API_HOST + '/' + ref_id).json()
            ref_exists = ref.status_code == 200
            if ref_exists:
                res = put(API_HOST + '/' + user_id, data={'ref':ref_id}).json()
                if res.status_code == 200:
                    print('Updated user referral')
                    return increment_referee_count(user_id, ref_id, ref.data)
                else:
                    print('Error saving referral')
            else:
                print('Invalid referral')
        else:
            print('User is already referred')

def update_step(user_id:str, step:str):
    res = put(API_HOST + '/' + user_id, data={'step':step}).json()
    if res.status_code == 200:
        print('Updated user step')
        return step
    else:
        print('Error saving step')

def fetch_step(user_id:str):
    user = get('%s/%s' % (API_HOST, user_id)).json()
    user_exists = user.status_code == 200

    if user_exists:
        return user.data.step
    else: 
        return None

