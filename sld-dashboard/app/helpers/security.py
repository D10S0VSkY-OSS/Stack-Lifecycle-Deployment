from cryptography.fernet import Fernet

from .config.api import settings


def vault_encrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        # Handle both str and bytes
        if isinstance(data, bytes):
            token = f.encrypt(data)
        else:
            token = f.encrypt(data.encode("utf-8"))
        return token.decode("utf-8")

    return wrap


def vault_decrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        # Handle both str and bytes
        if isinstance(data, bytes):
            token = f.decrypt(data)
        else:
            token = f.decrypt(data.encode("utf-8"))
        return token.decode("utf-8")

    return wrap
