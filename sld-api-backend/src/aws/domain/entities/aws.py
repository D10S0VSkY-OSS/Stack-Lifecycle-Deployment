import datetime
from typing import Any

from pydantic import BaseModel, SecretStr, constr


class AwsBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    access_key_id: constr(strip_whitespace=True)
    secret_access_key: constr(strip_whitespace=True)
    default_region: constr(strip_whitespace=True)
    extra_variables: dict[str, Any] | None = None


class AwsAsumeProfile(AwsBase):
    role_arn: constr(strip_whitespace=True) | None = None


class AwsId(BaseModel):
    id: int | None = None

    class Config:
        from_attributes = True


class AwsAccountResponseBase(BaseModel):
    id: int
    squad: str
    environment: str
    default_region: str | None
    role_arn: str | None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

    class Config:
        from_attributes = True


class AwsAccountResponse(AwsAccountResponseBase):
    extra_variables: dict[str, SecretStr] | None

    class Config:
        from_attributes = True


class AwsAccountResponseRepo(AwsAccountResponseBase):
    access_key_id: str
    secret_access_key: str
    extra_variables: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class AwsAccount(BaseModel):
    squad: str | None = None
    environment: str | None = None
    default_region: str | None = None
    role_arn: str | None = None
    access_key_id: str | None = None


class AwsAccountFilter(AwsAccount, AwsId):
    pass


class AwsAccountUpdate(AwsAccount):
    secret_access_key: str | None = None
    extra_variables: dict[str, Any] | None = None
