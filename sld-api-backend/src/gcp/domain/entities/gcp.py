from pydantic import BaseModel, constr


class GcloudBase(BaseModel):
    squad: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    gcloud_keyfile_json: dict


class Gcloud(GcloudBase):
    id: int

    class Config:
        from_attributes = True

class GcloudResponse(BaseModel):
    id: int
    squad: str
    environment: str
