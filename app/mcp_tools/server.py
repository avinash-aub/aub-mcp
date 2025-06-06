import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.mcp_tools.tools import mcp
from app.models import Base

load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine_sync = create_engine(database_url)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine_sync)

    print("✅ MCP server has started on http://127.0.0.1:5005")

    mcp.run()
