from pydantic import BaseModel, constr




class AzureBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    subscription_id: constr(strip_whitespace=True)
    client_id: constr(strip_whitespace=True)
    client_secret: constr(strip_whitespace=True)
    tenant_id: constr(strip_whitespace=True)


class Azure(AzureBase):
    id: int

    class Config:
        orm_mode = True
