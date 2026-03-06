from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityResponse
from app.schemas.building import BuildingResponse


class OrganizationResponse(BaseModel):
    id: int
    name: str
    phones: list[str]
    building: BuildingResponse
    activities: list[ActivityResponse]

    model_config = ConfigDict(from_attributes=True)
