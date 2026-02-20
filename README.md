# POC FalkorDB + PostgreSQL

This project is a Proof of Concept (POC) that combines a relational database (**PostgreSQL**) with a graph database (**FalkorDB**) to manage projects and recommend technologies.

## 🚀 Getting Started

The entire project is dockerized, so you only need to have Docker and Docker Compose installed.

### 1. Spin up the services
Run the following command in the project root:

```bash
docker-compose up --build
```

This command will:
- Build the Python application image using `uv` for ultra-fast dependency installation.
- Start a **PostgreSQL** container (port 5432).
- Start a **FalkorDB** container (port 6379).
- Start the **FastAPI** application (port 8000).

### 2. Populate the database (Seed)
Once the containers are running, you can insert sample data by running the seed script:

```bash
uv run seed.py
```

### 3. Access the application
Open your browser at:
👉 [http://localhost:8000](http://localhost:8000)

## 🛠️ Technologies Used in the seed

- **FastAPI**: Modern, high-performance web framework for Python.
- **SQLAlchemy**: For managing persistent data in PostgreSQL.
- **FalkorDB**: High-performance graph database for the recommendation engine.
- **UV**: Extremely fast Python package manager.
- **Docker**: To orchestrate all services.

## 📁 Main Structure

- `main.py`: FastAPI server and web interface (HTML/JS).
- `database.py`: Postgres models and FalkorDB client.
- `recommender.py`: Recommendation logic using Cypher queries.
- `seed.py`: Script to insert sample data.
- `docker-compose.yml`: Infrastructure configuration.
