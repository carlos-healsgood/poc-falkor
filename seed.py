import uuid
from sqlalchemy.orm import Session
from database import SessionLocal, Project, FalkorDBClient, Base, engine

def seed_data():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    falkor_client = FalkorDBClient()
    
    # Sample data
    projects_data = [
        ("E-commerce App", "A full-stack online store", ["Python", "FastAPI", "PostgreSQL", "React", "Docker"]),
        ("Weather Tracker", "Real-time weather monitoring", ["Python", "FastAPI", "Redis", "Docker"]),
        ("Crypto Wallet", "Blockchain wallet manager", ["React", "PostgreSQL", "Docker", "Node.js"]),
        ("Social Network", "Connect with friends", ["Python", "PostgreSQL", "Redis", "React"]),
        ("Task Manager", "Organize daily tasks", ["FastAPI", "PostgreSQL", "Vue.js", "Docker"]),
        ("Fitness Tracker", "Track workouts and diet", ["Python", "FastAPI", "PostgreSQL", "Docker"]),
        ("Blog Engine", "Custom CMS platform", ["Python", "SQLAlchemy", "PostgreSQL", "React"]),
        ("Chat App", "Real-time messaging", ["FastAPI", "Redis", "WebSockets", "React"]),
        ("IoT Dashboard", "Monitor sensor data", ["Python", "PostgreSQL", "FalkorDB", "Docker"]),
        ("Analytics Tool", "Data visualization platform", ["Python", "FastAPI", "PostgreSQL", "Docker", "D3.js"]),
    ]

    print("Seeding data...")

    try:
        for name, desc, techs in projects_data:
            # 1. Save to Postgres
            project = Project(name=name, description=desc)
            db.add(project)
            db.commit()
            db.refresh(project)
            
            # 2. Create Project node in FalkorDB
            falkor_client.create_project_node(project.id, project.name)
            
            # 3. Create Technology nodes and USES relationships
            for tech in techs:
                # Merge Technology node (creates if doesn't exist)
                falkor_client.graph.query(
                    "MERGE (t:Technology {name: $name})", 
                    {"name": tech}
                )
                
                # Create USES relationship
                falkor_client.graph.query(
                    """
                    MATCH (p:Project {id: $pid}), (t:Technology {name: $tname})
                    MERGE (p)-[:USES]->(t)
                    """,
                    {"pid": str(project.id), "tname": tech}
                )
            
            print(f"Added project: {name}")

        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
