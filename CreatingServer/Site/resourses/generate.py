import random
from transliterate import translit


def generate_password(length=8):
    chars = '+-/*!&$@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 8

    password = ''
    for i in range(length):
        password += random.choice(chars)
    return password


def generate_login(first_name='a', second_name=None):
    text = f"{first_name[0]}.{second_name}"
    login = translit(text, 'ru', reversed=True)
    return login
