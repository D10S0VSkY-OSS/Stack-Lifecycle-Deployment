import datetime
from typing import Any

from pydantic import BaseModel, SecretStr, constr


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
    scopes: list[str] | None = None
    subject_type: str | None = None
    token_introspection_uri: str | None = None
    revoke_uri: str | None = None


class GcloudBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    gcloud_keyfile_json: dict[str, str]
    extra_variables: dict[str, Any] | None = None


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
    extra_variables: dict[str, SecretStr] | None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

    class Config:
        from_attributes = True


class GcloudResponseRepo(BaseModel):
    id: int
    squad: str
    environment: str
    gcloud_keyfile_json: str
    extra_variables: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class GcloudAccountFilter(BaseModel):
    id: int | None = None
    squad: str | None = None
    environment: str | None = None

    class Config:
        from_attributes = True


class GcloudAccountUpdate(BaseModel):
    squad: str | None = None
    environment: str | None = None
    gcloud_keyfile_json: dict[str, Any] | None = None
    extra_variables: dict[str, Any] | None = None
