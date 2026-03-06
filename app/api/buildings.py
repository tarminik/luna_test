from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import haversine_distance, rect_filter, require_api_key
from app.core.db import get_session
from app.models.building import Building
from app.models.organization import Organization
from app.schemas import BuildingResponse, OrganizationResponse

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid or missing API key"}},
)


@router.get(
    "/search/in_radius",
    response_model=list[BuildingResponse],
    summary="Здания в радиусе",
    description="Поиск зданий в заданном радиусе (метры) от точки по формуле Haversine.",
)
async def buildings_in_radius(
    lat: float = Query(..., description="Широта центра поиска"),
    lon: float = Query(..., description="Долгота центра поиска"),
    radius_m: float = Query(..., gt=0, description="Радиус поиска в метрах"),
    session: AsyncSession = Depends(get_session),
):
    dist = haversine_distance(lat, lon)
    stmt = select(Building).where(dist <= radius_m)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/search/in_rect",
    response_model=list[BuildingResponse],
    summary="Здания в прямоугольнике",
    description="Поиск зданий внутри заданного прямоугольника координат.",
)
async def buildings_in_rect(
    lat_min: float = Query(...),
    lon_min: float = Query(...),
    lat_max: float = Query(...),
    lon_max: float = Query(...),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Building).where(rect_filter(lat_min, lon_min, lat_max, lon_max))
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{building_id}/organizations",
    response_model=list[OrganizationResponse],
    summary="Организации в здании",
    description="Список всех организаций, расположенных в указанном здании.",
)
async def organizations_in_building(
    building_id: int,
    session: AsyncSession = Depends(get_session),
):
    building = await session.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    stmt = (
        select(Organization)
        .where(Organization.building_id == building_id)
        .options(selectinload(Organization.building), selectinload(Organization.activities))
    )
    result = await session.execute(stmt)
    return result.scalars().all()
