from sqlalchemy import create_engine

from app.mcp_tools.tools import mcp
from app.models import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/realestate_mcp"
engine_sync = create_engine(DATABASE_URL)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine_sync)

    print("✅ MCP server has started on http://127.0.0.1:5005")

    mcp.run()
