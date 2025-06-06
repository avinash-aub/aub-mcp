# MCP Client and Backend Service

A comprehensive Multi-Client Protocol (MCP) implementation featuring both client and server components for resource management and API interactions.

## Features

- **MCP Client**
  - Connect to MCP servers
  - List and manage available resources
  - Read resource contents
  - Python-based API for easy integration

- **Backend Service**
  - FastAPI-based web server
  - RESTful API endpoints
  - Real-time updates with WebSocket support
  - Environment-based configuration

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aub-mcp
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Getting Started

### MCP Client

1. Make the run script executable:
   ```bash
   chmod +x run_mcp.sh
   ```

2. Run the MCP client:
   ```bash
   ./run_mcp.sh
   ```

### Backend Server

To start the backend development server:

```bash
uvicorn app.main:app --port 8005 --reload
```

The server will be available at `http://localhost:8005`

### Database Setup

To seed the database with initial data:

```bash
python seed_db.py
```

## Project Structure

```
aub-mcp/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── routes.py           # API route definitions
│   └── mcp_tools/          # MCP tools and utilities
│       ├── __init__.py
│       └── tools.py        # Core tool implementations
├── config/                 # Configuration files
├── mcp_client.py           # MCP client implementation
├── requirements.txt        # Python dependencies
├── run_mcp.sh             # Script to run MCP client
├── seed_db.py             # Database seeding script
└── .env                   # Environment variables
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
