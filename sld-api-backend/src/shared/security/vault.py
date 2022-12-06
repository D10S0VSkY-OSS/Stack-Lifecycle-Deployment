from config.api import settings
from cryptography.fernet import Fernet
from passlib.context import CryptContext


def vault_encrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        token = f.encrypt(bytes(data, "utf-8"))
        return token.decode("utf-8")

    return wrap


def vault_decrypt(func):
    def wrap(*args, **kwargs):
        key = settings.SECRET_VAULT
        f = Fernet(key)
        data = func(*args, **kwargs)
        token = f.decrypt(bytes(data, "utf-8"))
        return token.decode("utf-8")

    return wrap


def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
