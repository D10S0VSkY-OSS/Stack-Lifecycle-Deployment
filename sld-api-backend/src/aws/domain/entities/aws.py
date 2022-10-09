from typing import Optional

from pydantic import BaseModel, Field, constr


class AwsBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    access_key_id: constr(strip_whitespace=True)
    secret_access_key: Optional[constr(strip_whitespace=True)] = Field(
        None, example="string"
    )
    default_region: constr(strip_whitespace=True)


class AwsAsumeProfile(AwsBase):
    profile_name: Optional[constr(strip_whitespace=True)] = None
    role_arn: Optional[constr(strip_whitespace=True)] = None
    source_profile: Optional[constr(strip_whitespace=True)] = None


class Aws(AwsBase):
    id: int

    class Config:
        orm_mode = True
