from pydantic import BaseModel, Field, constr


class ScheduleUpdate(BaseModel):
    start_time: constr(strip_whitespace=True) | None = Field(None, example="30 7 * * 0-4")
    destroy_time: constr(strip_whitespace=True) | None = Field(None, example="30 18 * * 0-4")
