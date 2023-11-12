from pydantic import BaseModel, constr


class ActivityLogs(BaseModel):
    id: int
    username: constr(strip_whitespace=True)
    squad: constr(strip_whitespace=True)
    action: constr(strip_whitespace=True)

    class Config:
        from_attributes = True
