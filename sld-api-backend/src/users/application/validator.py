from typing import Tuple

from dependency_injector import containers, providers
from password_strength import PasswordPolicy
from python_usernames import is_safe_username


class PasswordValidator:
    def __init__(self) -> None:
        self._policy = PasswordPolicy.from_names(
            length=8, uppercase=1, numbers=1, special=1, nonletters=1
        )

    def validate(self, password: str) -> bool:
        if password == None or len(password) == 0:
            return False
        if len(self._policy.test(password)) > 0:
            return False
        return True


class UsernameValidator:
    def __init__(self) -> None:
        self._whitelist = ["admin"]
        self._black_list = ["guest", "root", "administrator"]
        self._max_length = 12

    def validate(self, username: str) -> bool:
        print(username)
        return is_safe_username(
            username,
            whitelist=self._whitelist,
            blacklist=self._black_list,
            max_length=self._max_length,
        )


class UserService:
    def __init__(
        self,
        username_validator: UsernameValidator,
        password_validator: PasswordValidator,
    ):
        self.username_validator = username_validator
        self.password_validator = password_validator

    def validate(self, username: str, password: str) -> Tuple[str, str]:
        if not self.password_validator.validate(password):
            return (False, "Password weak")
        elif not self.username_validator.validate(username):
            return (False, "User invalid")
        return (True, "")


class Container(containers.DeclarativeContainer):
    username_validator = providers.Singleton(UsernameValidator)
    password_validator = providers.Singleton(PasswordValidator)

    user_service = providers.Singleton(
        UserService, username_validator, password_validator
    )
