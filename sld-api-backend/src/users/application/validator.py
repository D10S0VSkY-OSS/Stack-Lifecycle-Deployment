import re

from dependency_injector import containers, providers
from password_strength import PasswordPolicy


def is_safe_username(
    username: str, whitelist: list = None, blacklist: list = None, max_length: int = 20
) -> bool:
    """
    Validate username safety.
    Replacement for python_usernames.is_safe_username

    Rules:
    - Only alphanumeric characters, underscore, and hyphen
    - Must start with a letter
    - Length between 3 and max_length
    - Not in blacklist (unless in whitelist)
    """
    if not username:
        return False

    # Check whitelist first (bypasses all other checks)
    if whitelist and username.lower() in [w.lower() for w in whitelist]:
        return True

    # Check blacklist
    if blacklist and username.lower() in [b.lower() for b in blacklist]:
        return False

    # Length validation
    if len(username) < 3 or len(username) > max_length:
        return False

    # Pattern validation: alphanumeric, underscore, hyphen
    # Must start with a letter
    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    if not re.match(pattern, username):
        return False

    return True


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

    def validate(self, username: str, password: str) -> tuple[str, str]:
        if not self.password_validator.validate(password):
            return (False, "Password weak")
        elif not self.username_validator.validate(username):
            return (False, "User invalid")
        return (True, "")


class Container(containers.DeclarativeContainer):
    username_validator = providers.Singleton(UsernameValidator)
    password_validator = providers.Singleton(PasswordValidator)

    user_service = providers.Singleton(UserService, username_validator, password_validator)
