import hmac
import math

from fastapi import Header, HTTPException
from sqlalchemy import ColumnElement, and_, func

from app.core.config import get_settings
from app.models.building import Building

EARTH_RADIUS_M = 6_371_000


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None or not hmac.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def haversine_distance(lat: float, lon: float) -> ColumnElement[float]:
    """SQLAlchemy expression: distance in meters from (lat, lon) to Building."""
    lat_r = func.radians(Building.latitude)
    lon_r = func.radians(Building.longitude)
    lat2_r = math.radians(lat)
    lon2_r = math.radians(lon)

    dlat = lat_r - lat2_r
    dlon = lon_r - lon2_r

    a = func.pow(func.sin(dlat / 2), 2) + math.cos(lat2_r) * func.cos(lat_r) * func.pow(
        func.sin(dlon / 2), 2
    )
    return 2 * EARTH_RADIUS_M * func.asin(func.sqrt(a))


def rect_filter(
    lat_min: float, lon_min: float, lat_max: float, lon_max: float
) -> ColumnElement[bool]:
    return and_(
        Building.latitude >= lat_min,
        Building.latitude <= lat_max,
        Building.longitude >= lon_min,
        Building.longitude <= lon_max,
    )
