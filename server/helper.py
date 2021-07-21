from firebase_admin import db

def get_user_reference(user_id):
    user = db.reference('users/%s' % user_id)
    return user

def get_user(user_id):
    user_ref = get_user_reference(user_id)
    return user_ref.get()

def update_user(user_id, data):
    user_ref = get_user_reference(user_id)
    try:
        user_ref.update(data)
        return True
    except:
        return False
