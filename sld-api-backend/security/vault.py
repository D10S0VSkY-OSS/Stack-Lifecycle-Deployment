from cryptography.fernet import Fernet

from config.api import settings


def vault_encrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        token = f.encrypt(bytes(data, 'utf-8'))
        return token.decode('utf-8')
    return wrap


def vault_decrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        token = f.decrypt(bytes(data, 'utf-8'))
        return token.decode('utf-8')
    return wrap
