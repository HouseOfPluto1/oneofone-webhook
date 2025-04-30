# settings_manager.py

user_settings = {}

def set_setting(user_id, key, value):
    user_settings.setdefault(user_id, {})[key] = value

def get_user_settings(user_id):
    return user_settings.get(user_id, {
        "copies": 1,
        "crop": 10,
        "flip": False
    })

def reset_user_settings(user_id):
    if user_id in user_settings:
        del user_settings[user_id]
