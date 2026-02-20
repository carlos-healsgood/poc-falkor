from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import database
import recommender

app = FastAPI()

# Create database tables
database.Base.metadata.create_all(bind=database.engine)

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]

@app.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = database.save_project_to_both(db, name=project.name, description=project.description)
    return {
        "id": str(db_project.id),
        "name": db_project.name,
        "description": db_project.description
    }

@app.get("/suggest")
def suggest(name: str):
    return recommender.suggest_technologies(name)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FalkorDB Project Recommender</title>
        <style>
            body { font-family: sans-serif; margin: 40px; }
            .badge { 
                display: inline-block; 
                padding: 5px 10px; 
                margin: 5px; 
                background-color: #007bff; 
                color: white; 
                border-radius: 15px; 
                cursor: pointer; 
                text-decoration: none;
            }
            .badge:hover { background-color: #0056b3; }
            #suggestions { margin-top: 20px; }
            input { padding: 10px; width: 300px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h1>Project Search & Recommendations</h1>
        <p>Type a project name to see suggested technologies:</p>
        <input type="text" id="projectName" placeholder="Enter project name..." onkeyup="getSuggestions()">
        
        <div id="suggestions"></div>

        <script>
            async function getSuggestions() {
                const name = document.getElementById('projectName').value;
                if (name.length < 2) {
                    document.getElementById('suggestions').innerHTML = '';
                    return;
                }
                
                try {
                    const response = await fetch(`/suggest?name=${encodeURIComponent(name)}`);
                    const data = await response.json();
                    
                    const suggestionsDiv = document.getElementById('suggestions');
                    suggestionsDiv.innerHTML = '';
                    
                    if (data.length === 0) {
                        suggestionsDiv.innerHTML = '<p style="color: gray;">No recommendations found.</p>';
                        return;
                    }
                    
                    data.forEach(item => {
                        const span = document.createElement('span');
                        span.className = 'badge';
                        span.innerText = `${item.technology} (${item.score})`;
                        span.onclick = () => alert(`You clicked ${item.technology}`);
                        suggestionsDiv.appendChild(span);
                    });
                } catch (error) {
                    console.error('Error fetching suggestions:', error);
                }
            }
        </script>
    </body>
    </html>
    """
