def extract_referral(message:str) -> str:
    ref = message.split()
    r_v = ref[1] if len(ref) > 1 else ""
    return r_v


def in_storage(unique_code):
    # (pseudo-code) Should check if a unique code exists in storage
    return True


def get_username_from_storage(unique_code):
    # (pseudo-code) Does a query to the storage, retrieving the associated username
    # Should be replaced by a real database-lookup.
    return "ABC" if in_storage(unique_code) else None


def save_chat_id(chat_id, username):
    # (pseudo-code) Save the chat_id->username to storage
    # Should be replaced by a real database query.
    pass
