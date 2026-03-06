from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_api_key
from app.core.db import get_session
from app.models.activity import Activity
from app.models.organization import Organization, organization_activity
from app.schemas import OrganizationResponse

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid or missing API key"}},
)


@router.get(
    "/{activity_id}/organizations",
    response_model=list[OrganizationResponse],
    summary="Организации по виду деятельности",
    description="Возвращает организации, связанные с указанным видом деятельности "
    "и всеми его дочерними видами (рекурсивно).",
)
async def organizations_by_activity(
    activity_id: int,
    session: AsyncSession = Depends(get_session),
):
    activity = await session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # WITH RECURSIVE CTE
    base = select(Activity.id).where(Activity.id == activity_id).cte(
        name="activity_tree", recursive=True
    )
    recursive = select(Activity.id).join(base, Activity.parent_id == base.c.id)
    cte = base.union_all(recursive)

    stmt = (
        select(Organization)
        .join(organization_activity, Organization.id == organization_activity.c.organization_id)
        .where(organization_activity.c.activity_id.in_(select(cte.c.id)))
        .options(selectinload(Organization.building), selectinload(Organization.activities))
        .distinct()
    )
    result = await session.execute(stmt)
    return result.scalars().all()
