from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import haversine_distance, rect_filter, require_api_key
from app.core.db import get_session
from app.models.building import Building
from app.models.organization import Organization
from app.schemas import OrganizationResponse

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid or missing API key"}},
)

_org_eager = [selectinload(Organization.building), selectinload(Organization.activities)]


@router.get(
    "/search",
    response_model=list[OrganizationResponse],
    summary="Поиск организации по имени",
    description="Поиск организаций по подстроке в названии (регистронезависимый).",
)
async def search_by_name(
    name: str = Query(..., min_length=1, description="Подстрока для поиска в названии"),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Organization).where(Organization.name.ilike(f"%{name}%")).options(*_org_eager)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/search/in_radius",
    response_model=list[OrganizationResponse],
    summary="Организации в радиусе",
    description="Поиск организаций, расположенных в зданиях в заданном радиусе от точки.",
)
async def organizations_in_radius(
    lat: float = Query(..., description="Широта центра поиска"),
    lon: float = Query(..., description="Долгота центра поиска"),
    radius_m: float = Query(..., gt=0, description="Радиус поиска в метрах"),
    session: AsyncSession = Depends(get_session),
):
    dist = haversine_distance(lat, lon)
    stmt = (
        select(Organization)
        .join(Building)
        .where(dist <= radius_m)
        .options(*_org_eager)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/search/in_rect",
    response_model=list[OrganizationResponse],
    summary="Организации в прямоугольнике",
    description="Поиск организаций, расположенных в зданиях внутри прямоугольника координат.",
)
async def organizations_in_rect(
    lat_min: float = Query(...),
    lon_min: float = Query(...),
    lat_max: float = Query(...),
    lon_max: float = Query(...),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Organization)
        .join(Building)
        .where(rect_filter(lat_min, lon_min, lat_max, lon_max))
        .options(*_org_eager)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Организация по ID",
    description="Получение полной информации об организации по её идентификатору.",
)
async def get_organization(
    organization_id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Organization).where(Organization.id == organization_id).options(*_org_eager)
    result = await session.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
