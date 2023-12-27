from typing import Optional, Dict, Any

from pydantic import BaseModel, constr


class AwsBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    access_key_id: constr(strip_whitespace=True)
    secret_access_key: constr(strip_whitespace=True)
    default_region: constr(strip_whitespace=True)
    extra_variables: Optional[Dict[str, Any]] = None


class AwsAsumeProfile(AwsBase):
    role_arn: Optional[constr(strip_whitespace=True)] = None


class Aws(AwsBase):
    id: int

    class Config:
        from_attributes = True


class AwsAccountResponse(BaseModel):
    id: int
    squad: str
    environment: str
    default_region: Optional[str]
    role_arn: Optional[str]
    extra_variables: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AwsAccountResponseRepo(AwsAccountResponse):
    access_key_id: str
    secret_access_key: str

    class Config:
        from_attributes = True


class AwsAccountFilter(BaseModel):
    id: Optional[int] = None
    squad: Optional[str] = None
    access_key_id: Optional[str] = None
    environment: Optional[str] = None
    default_region: Optional[str] = None
    role_arn: Optional[str] = None
