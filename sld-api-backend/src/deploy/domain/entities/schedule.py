from typing import Optional

from pydantic import BaseModel, Field, constr


class ScheduleUpdate(BaseModel):
    start_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 7 * * 0-4"
    )
    destroy_time: Optional[constr(strip_whitespace=True)] = Field(
        None, example="30 18 * * 0-4"
    )
