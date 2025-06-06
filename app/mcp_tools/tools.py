import os
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.utils import format_property_details

load_dotenv()

mcp = FastMCP(
    "Real Estate MCP",
)

engine_sync = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine_sync)


@mcp.tool()
def search_properties(
    city: Optional[str] = None,
    bhk: Optional[int] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    limit: int = 20,
) -> dict:
    """
    Search properties using raw SQL.
    Input can include city, bhk, max_price, min_price, and limit.
    """
    session = SessionLocal()
    try:
        query = """
        SELECT id, no_of_bedrooms, no_of_bathrooms, carpet_area, total_area,
               country, state, city, community, building_name, asking_price
        FROM properties
        WHERE 1=1
        """
        params = {}

        if city:
            query += " AND city ILIKE :city"
            params["city"] = f"%{city}%"
        if bhk is not None:
            query += " AND no_of_bedrooms = :bhk"
            params["bhk"] = bhk
        if max_price is not None:
            query += " AND asking_price <= :max_price"
            params["max_price"] = max_price
        if min_price is not None:
            query += " AND asking_price >= :min_price"
            params["min_price"] = min_price

        query += " LIMIT :limit"
        params["limit"] = limit

        result = session.execute(text(query), params)
        results = [dict(row) for row in result.mappings().all()]
        formatted_results = format_property_details(results)
    finally:
        session.close()

    if not results:
        return {
            "message": "No properties found",
            "data": [],
        }

    return {
        "message": f"{len(results)} Properties found",
        "data": formatted_results,
    }
