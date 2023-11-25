from pydantic import BaseModel, constr


class CustomProviderBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    configuration: dict


class CustomProvider(CustomProviderBase):
    id: int

    class Config:
        from_attributes = True

class CustomProviderResponse(BaseModel):
    id: int
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
