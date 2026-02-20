import uuid
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker
from falkordb import FalkorDB

# Postgres Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/project_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

# FalkorDB Setup
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", 6379))

class FalkorDBClient:
    def __init__(self):
        self.db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        self.graph = self.db.select_graph("projects_graph")

    def create_project_node(self, project_id: str, name: str):
        query = "CREATE (:Project {id: $id, name: $name})"
        params = {"id": str(project_id), "name": name}
        self.graph.query(query, params)

# Utility function
def save_project_to_both(db_session, name: str, description: str = None):
    # 1. Save to Postgres
    new_project = Project(name=name, description=description)
    db_session.add(new_project)
    db_session.commit()
    db_session.refresh(new_project)

    # 2. Save to FalkorDB
    falkor_client = FalkorDBClient()
    falkor_client.create_project_node(new_project.id, new_project.name)

    return new_project
