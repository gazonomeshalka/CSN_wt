import os
import hashlib


def create_key(password):
    salt = os.urandom(32)
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    key = salt + new_key
    return key


def check_password(password, key_in_data):
    salt = key_in_data[:32]
    old_key = key_in_data[32:]
    new_key = hashlib.pbkdf2_hmac('sha256',
                                  password.encode('utf-8'),
                                  salt,
                                  100000)
    if old_key == new_key:
        return True
    else:
        return False
