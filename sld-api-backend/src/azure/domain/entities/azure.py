import datetime
from typing import Any

from pydantic import BaseModel, SecretStr, constr


class AzureBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    client_id: constr(strip_whitespace=True)
    client_secret: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)
    extra_variables: dict[str, Any] | None = None


class AzureId(BaseModel):
    id: int | None = None

    class Config:
        from_attributes = True


class AzureAccountResponseBase(AzureId):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


class AzureAccountResponse(AzureAccountResponseBase):
    extra_variables: dict[str, SecretStr] | None

    class Config:
        from_attributes = True


class AzureAccountResponseRepo(AzureAccountResponseBase):
    client_id: str
    client_secret: str
    extra_variables: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class AzureAccount(BaseModel):
    squad: str | None = None
    access_key_id: str | None = None
    environment: str | None = None
    client_id: str | None = None
    subscription_id: str | None = None
    tenant_id: str | None = None


class AzureAccountFilter(AzureAccount, AzureId):
    pass


class AzureAccountUpdate(AzureAccount):
    client_secret: str | None = None
    extra_variables: dict[str, Any] | None = None
