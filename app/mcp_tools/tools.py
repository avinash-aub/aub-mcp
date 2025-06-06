import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, func, text
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
    Search for properties based on the provided filters.

    Args:
        city (str, optional): City name to filter by.
        bhk (int, optional): Number of bedrooms to filter by.
        max_price (int, optional): Maximum price to filter by.
        min_price (int, optional): Minimum price to filter by.
        limit (int, optional): Maximum number of results to return.

    Returns:
        dict: Detailed property information including all available fields
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


@mcp.tool()
def get_property_details(property_id: int) -> dict:
    """
    Get detailed information about a specific property by its ID.
    
    Args:
        property_id: The unique identifier of the property
        
    Returns:
        dict: Detailed property information including all available fields
    """
    session = SessionLocal()
    try:
        query = """
        SELECT *
        FROM properties
        WHERE id = :property_id
        """
        result = session.execute(text(query), {"property_id": property_id})
        property_data = result.mappings().first()

        if not property_data:
            return {"message": "Property not found", "data": {}}

        return {
            "message": "Property details retrieved successfully",
            "data": dict(property_data)
        }
    finally:
        session.close()


@mcp.tool()
def compare_properties(property_ids: List[int]) -> dict:
    """
    Compare multiple properties side by side.
    
    Args:
        property_ids: List of property IDs to compare
        
    Returns:
        dict: Comparison of the specified properties
    """
    if len(property_ids) < 2:
        return {"message": "Please provide at least 2 property IDs to compare", "data": []}

    session = SessionLocal()
    try:
        placeholders = ", ".join([":id_" + str(i) for i in range(len(property_ids))])
        params = {"id_" + str(i): pid for i, pid in enumerate(property_ids)}

        query = f"""
        SELECT id, building_name, no_of_bedrooms, no_of_bathrooms, 
               carpet_area, total_area, asking_price, city, community
        FROM properties
        WHERE id IN ({placeholders})
        """

        result = session.execute(text(query), params)
        properties = [dict(row) for row in result.mappings().all()]

        if len(properties) < 2:
            return {"message": "Not enough valid property IDs found", "data": []}

        return {
            "message": f"Comparison of {len(properties)} properties",
            "data": properties
        }
    finally:
        session.close()


@mcp.tool()
def get_price_trends(
        city: str,
        days: int = 30,
        property_type: Optional[str] = None
) -> dict:
    """
    Get price trends for properties in a specific city over time.
    
    Args:
        city: City to analyze price trends for
        days: Number of days to look back (default: 30)
        property_type: Optional property type filter (e.g., 'apartment', 'villa')
        
    Returns:
        dict: Price trend data
    """
    session = SessionLocal()
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = """
        SELECT 
            AVG(asking_price) as avg_price,
            COUNT(*) as property_count
        FROM properties
        WHERE city ILIKE :city
        """

        params = {
            "city": f"%{city}%",
        }

        if property_type:
            query += " AND property_type = :property_type"
            params["property_type"] = property_type.lower()

        result = session.execute(text(query), params)
        trends = [dict(row) for row in result.mappings().all()]

        return {
            "message": f"Price trends for {city}",
            "data": trends,
            "time_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    finally:
        session.close()


@mcp.tool()
def get_similar_properties(
        property_id: int,
        limit: int = 5
) -> dict:
    """
    Find properties similar to a given property ID.
    
    Args:
        property_id: The property ID to find similar properties for
        limit: Maximum number of similar properties to return (default: 5)
        
    Returns:
        dict: List of similar properties
    """
    session = SessionLocal()
    try:
        # First, get the reference property details
        ref_query = """
        SELECT city, no_of_bedrooms, asking_price, property_type
        FROM properties
        WHERE id = :property_id
        """
        ref_prop = session.execute(text(ref_query), {"property_id": property_id}).mappings().first()

        if not ref_prop:
            return {"message": "Reference property not found", "data": []}

        ref_prop = dict(ref_prop)

        # Find similar properties
        similar_query = """
        SELECT *,
               ABS(no_of_bedrooms - :ref_bhk) as bhk_diff,
               ABS(asking_price - :ref_price) / NULLIF(:ref_price, 0) * 100 as price_diff_pct
        FROM properties
        WHERE id != :property_id
          AND city = :city
          AND property_type = :prop_type
        ORDER BY bhk_diff, price_diff_pct
        LIMIT :limit
        """

        params = {
            "property_id": property_id,
            "city": ref_prop["city"],
            "prop_type": ref_prop["property_type"],
            "ref_bhk": ref_prop["no_of_bedrooms"],
            "ref_price": ref_prop["asking_price"],
            "limit": limit
        }

        result = session.execute(text(similar_query), params)
        similar_properties = [dict(row) for row in result.mappings().all()]

        return {
            "message": f"Found {len(similar_properties)} similar properties",
            "reference_property_id": property_id,
            "data": similar_properties
        }
    finally:
        session.close()


@mcp.tool()
def get_community_stats(
        community: str,
        city: Optional[str] = None
) -> dict:
    """
    Get statistics for a specific community or neighborhood.
    
    Args:
        community: Name of the community/neighborhood
        city: Optional city filter for more specific results
        
    Returns:
        dict: Community statistics including average prices, property types, etc.
    """
    session = SessionLocal()
    try:
        query = """
        SELECT 
            COUNT(*) as total_properties,
            AVG(asking_price) as avg_price,
            MIN(asking_price) as min_price,
            MAX(asking_price) as max_price,
            AVG(no_of_bedrooms) as avg_bedrooms,
            AVG(no_of_bathrooms) as avg_bathrooms,
            property_type,
            COUNT(*) as count_by_type
        FROM properties
        WHERE community ILIKE :community
        """

        params = {"community": f"%{community}%"}

        if city:
            query += " AND city ILIKE :city"
            params["city"] = f"%{city}%"

        query += """
        GROUP BY property_type
        ORDER BY count_by_type DESC
        """

        result = session.execute(text(query), params)
        stats = [dict(row) for row in result.mappings().all()]

        if not stats:
            return {"message": f"No data found for community: {community}", "data": {}}

        return {
            "message": f"Statistics for {community}",
            "data": stats,
            "location": city if city else "All cities"
        }
    finally:
        session.close()
