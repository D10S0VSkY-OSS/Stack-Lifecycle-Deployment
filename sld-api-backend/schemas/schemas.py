from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    fullname: str
    password: str
    email: EmailStr = None
    squad: str
    is_active: bool = True
    privilege: bool = False
    master: bool = False


class UserCreateMaster(UserBase):
    fullname: str
    password: str
    email: EmailStr = None
    privilege: bool = False
    is_active: bool = True
    master: bool = False
    squad: str


class UserUpdate(UserCreate):
    pass


class UserAuthenticate(UserBase):
    password: str


class UserInit(BaseModel):
    password: str

class PasswordReset(BaseModel):
    passwd: str
    class  Config :
         orm_mode  =  True

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    token_type: str
    access_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class TokenData(BaseModel):
    username: str = None


class StackBase(BaseModel):
    stack_name: str
    git_repo: str
    branch: str = "master"
    squad_access: List[str] = "[*]"
    tf_version: str = "1.0.0"
    description: str


class StackCreate(StackBase):
    pass


class Stack(StackBase):
    id: int
    task_id: str
    user_id: int

    class Config:
        orm_mode = True


class AwsBase(BaseModel):
    squad: str
    environment: str
    access_key_id: str
    secret_access_key: Optional[str] = Field(None, example="string")
    default_region: str


class AwsAsumeProfile(AwsBase):
    profile_name: Optional[str] = None
    role_arn: Optional[str] = None
    source_profile: Optional[str] = None


class Aws(AwsBase):
    id: int

    class Config:
        orm_mode = True


class GcloudBase(BaseModel):
    squad: str
    environment: str
    gcloud_keyfile_json: dict


class Gcloud(GcloudBase):
    id: int

    class Config:
        orm_mode = True


class AzureBase(BaseModel):
    squad: str
    environment: str
    subscription_id: str
    client_id: str
    client_secret: str
    tenant_id: str


class Azure(AwsBase):
    id: int

    class Config:
        orm_mode = True


class DeployBase(BaseModel):
    name: str
    stack_name: str
    username: str
    squad: str
    environment: str
    variables: str


class DeployCreate(BaseModel):
    name: str
    squad: str
    stack_name: str
    environment: str
    start_time: Optional[str] = Field(None, example="30 7 * * 0-4")
    destroy_time: Optional[str] = Field(None, example="30 18 * * 0-4")
    variables: dict


class DeployCreateMaster(DeployCreate):
    squad: str


class DeployDeleteMaster(BaseModel):
    squad: str


class DeployUpdate(BaseModel):
    start_time: str
    destroy_time: str
    variables: dict


class Deploy(StackBase):
    id: int
    task_id: str
    user_id: int

    class Config:
        orm_mode = True

class PlanCreate(BaseModel):
    name: str
    stack_name: str
    squad: str
    environment: str
    variables: dict


class TasksBase(BaseModel):
    id: str
    deploy_id: str
    name: str

class ActivityLogs(BaseModel):
    id: int
    username: str
    squad: str
    action: str

    class Config:
        orm_mode = True
