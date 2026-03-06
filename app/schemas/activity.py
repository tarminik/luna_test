from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None

    model_config = ConfigDict(from_attributes=True)
