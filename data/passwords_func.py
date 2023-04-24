import os
import hashlib


def create_key(password):
    salt = os.urandom(32)  # создание соли
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # хеширование пароля
    key = salt + new_key  # преобразование в вид для хранения
    return key


def check_password(password, key_in_data):
    # отделение соли от хешированного пароля
    salt = key_in_data[:32]
    old_key = key_in_data[32:]
    # хеширование введенного пароля
    new_key = hashlib.pbkdf2_hmac('sha256',
                                  password.encode('utf-8'),
                                  salt,
                                  100000)
    if old_key == new_key:  # проверка на совпадение
        return True
    else:
        return False
