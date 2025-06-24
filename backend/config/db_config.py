import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain_community.utilities import SQLDatabase

# POINT TO data/ directory by default
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = os.getenv("DB_PATH", PROJECT_ROOT / "backend" / "data" / "synthetic_po.sqlite")

# Create a SQLAlchemy engine for the local file
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Wrap the engine in LangChain's SQLDatabase for toolkit usage
db = SQLDatabase(engine)
