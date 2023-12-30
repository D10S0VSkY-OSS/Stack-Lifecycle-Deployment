from pydantic import BaseModel, constr, SecretStr
from typing import Optional, Dict, Any
import datetime


class AzureBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    client_id: constr(strip_whitespace=True)
    client_secret: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)
    extra_variables: Optional[Dict[str, Any]] = None


class AzureId(BaseModel):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class AzureAccountResponseBase(AzureId):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class AzureAccountResponse(AzureAccountResponseBase):
    extra_variables: Optional[Dict[str, SecretStr]]

    class Config:
        from_attributes = True


class AzureAccountResponseRepo(AzureAccountResponseBase):
    client_id: str
    client_secret: str
    extra_variables: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AzureAccount(BaseModel):
    squad: Optional[str] = None
    access_key_id: Optional[str] = None
    environment: Optional[str] = None
    client_id: Optional[str] = None
    subscription_id: Optional[str] = None
    tenant_id: Optional[str] = None


class AzureAccountFilter(AzureAccount, AzureId):
    pass


class AzureAccountUpdate(AzureAccount):
    client_secret: Optional[str] = None
    extra_variables: Optional[Dict[str, Any]] = None
