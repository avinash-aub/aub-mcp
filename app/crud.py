from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Property


async def get_filtered_properties(
    db: AsyncSession,
    city: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bhk: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict]:
    """
    Async query to fetch properties for FastAPI.
    """
    filters = []

    if city:
        filters.append(Property.city.ilike(f"%{city}%"))
    if bhk:
        filters.append(Property.no_of_bedrooms == bhk)
    if max_price is not None:
        filters.append(Property.asking_price <= max_price)
    if min_price is not None:
        filters.append(Property.asking_price >= min_price)

    query = select(Property).where(and_(*filters)).limit(limit).offset(offset)
    result = await db.execute(query)
    properties = result.scalars().all()
    return [serialize_property(p) for p in properties]


def serialize_property(p: Property) -> Dict:
    """
    Convert Property object to dict.
    """
    return {
        "id": p.id,
        "no_of_bedrooms": p.no_of_bedrooms,
        "no_of_bathrooms": p.no_of_bathrooms,
        "carpet_area": p.carpet_area,
        "total_area": p.total_area,
        "country": p.country,
        "state": p.state,
        "city": p.city,
        "community": p.community,
        "building_name": p.building_name,
        "asking_price": p.asking_price,
    }
