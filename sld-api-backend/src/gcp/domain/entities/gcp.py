from pydantic import BaseModel, constr, SecretStr
from typing import Optional, Dict, Any, List
import datetime


class GCloudJson(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str
    scopes: Optional[List[str]] = None
    subject_type: Optional[str] = None
    token_introspection_uri: Optional[str] = None
    revoke_uri: Optional[str] = None


class GcloudBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    gcloud_keyfile_json: Dict[str, str]
    extra_variables: Optional[Dict[str, Any]] = None


class GcloudAccount(GcloudBase):
    pass


class Gcloud(GcloudBase):
    id: int

    class Config:
        from_attributes = True


class GcloudResponse(BaseModel):
    id: int
    squad: str
    environment: str
    extra_variables: Optional[Dict[str, SecretStr]]
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class GcloudResponseRepo(BaseModel):
    id: int
    squad: str
    environment: str
    gcloud_keyfile_json: str
    extra_variables: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class GcloudAccountFilter(BaseModel):
    id: Optional[int] = None
    squad: Optional[str] = None
    environment: Optional[str] = None

    class Config:
        from_attributes = True


class GcloudAccountUpdate(BaseModel):
    squad: Optional[str] = None
    environment: Optional[str] = None
    gcloud_keyfile_json: Optional[Dict[str, Any]] = None
    extra_variables: Optional[Dict[str, Any]] = None
