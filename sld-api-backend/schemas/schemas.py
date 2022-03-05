from pydantic import BaseModel, EmailStr, Field, ValidationError, validator, SecretStr, constr
from typing import Optional, List


class UserBase(BaseModel):
    username: constr(strip_whitespace=True)


class UserCreate(UserBase):
    fullname: constr(strip_whitespace=True)
    password: str
    email: EmailStr = None
    squad: List[str] = []
    role: List[str] = []
    is_active: bool = True


class UserCreateMaster(UserBase):
    fullname: constr(strip_whitespace=True)
    password: str
    email: EmailStr = None
    is_active: bool = True
    squad: List[str] = []
    role: List[str] = []


class UserUpdate(UserCreate):
    pass


class UserAuthenticate(UserBase):
    password: str


class UserInit(BaseModel):
    password: str


class PasswordReset(BaseModel):
    passwd: str

    class Config:
        orm_mode = True


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
    stack_name: constr(strip_whitespace=True)
    git_repo: constr(strip_whitespace=True)
    branch: constr(strip_whitespace=True)  = "master"
    squad_access: List[str] = ["*"]
    tf_version: constr(strip_whitespace=True) = "1.1.7"
    description: constr(strip_whitespace=True)


class StackCreate(StackBase):
    pass


class Stack(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        orm_mode = True


class AwsBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    access_key_id: constr(strip_whitespace=True)
    secret_access_key: Optional[constr(strip_whitespace=True)] = Field(None, example="string")
    default_region: constr(strip_whitespace=True)


class AwsAsumeProfile(AwsBase):
    profile_name: Optional[constr(strip_whitespace=True)] = None
    role_arn: Optional[constr(strip_whitespace=True)] = None
    source_profile: Optional[constr(strip_whitespace=True)] = None


class Aws(AwsBase):
    id: int

    class Config:
        orm_mode = True


class GcloudBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    gcloud_keyfile_json: dict


class Gcloud(GcloudBase):
    id: int

    class Config:
        orm_mode = True


class AzureBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    client_id: constr(strip_whitespace=True)
    client_secret: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)


class Azure(AwsBase):
    id: int

    class Config:
        orm_mode = True


class DeployBase(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    username: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    variables: constr(strip_whitespace=True)


class DeployCreate(BaseModel):
    name: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    start_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 7 * * 0-4")
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 18 * * 0-4")
    variables: dict


class DeployCreateMaster(DeployCreate):
    squad: constr(strip_whitespace=True)


class DeployDeleteMaster(BaseModel):
    squad: constr(strip_whitespace=True)


class DeployUpdate(BaseModel):
    start_time: constr(strip_whitespace=True)
    destroy_time: constr(strip_whitespace=True)
    variables: dict


class Deploy(StackBase):
    id: int
    task_id: constr(strip_whitespace=True)
    user_id: int

    class Config:
        orm_mode = True


class PlanCreate(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    start_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 7 * * 0-4")
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 18 * * 0-4")
    variables: dict


class TasksBase(BaseModel):
    id: str
    deploy_id: constr(strip_whitespace=True)
    name: constr(strip_whitespace=True)


class ActivityLogs(BaseModel):
    id: int
    username: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    action: constr(strip_whitespace=True)

    class Config:
        orm_mode = True


class ScheduleUpdate(BaseModel):
    start_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 7 * * 0-4")
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(None, example="30 18 * * 0-4")
