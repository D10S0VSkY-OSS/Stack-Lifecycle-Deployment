from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    username: constr(strip_whitespace=True)


class UserCreate(UserBase):
    fullname: constr(strip_whitespace=True)
    password: str
    email: EmailStr = None
    is_active: bool = True
    squad: List[str] = []
    role: List[str] = []


class UserCreateMaster(UserCreate):
    pass


class UserUpdate(UserCreate):
    pass


class UserAuthenticate(UserBase):
    password: str


class UserInit(BaseModel):
    password: str


class PasswordReset(BaseModel):
    passwd: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    token_type: str
    access_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class TokenData(BaseModel):
    username: str = None


class PlanCreate(BaseModel):
    name: constr(strip_whitespace=True)
    stack_name: constr(strip_whitespace=True)
    stack_branch: Optional[constr(strip_whitespace=True)] = Field("", example="")
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    start_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 7 * * 0-4"
    )
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 18 * * 0-4"
    )
    tfvar_file: Optional[constr(strip_whitespace=True)] = Field(
        "", example="terraform.tfvars"
    )
    project_path: Optional[constr(strip_whitespace=True)] = Field("", example="s")
    variables: dict
