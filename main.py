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
    technologies: List[str] = []

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]

@app.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = database.save_project_to_both(
        db, 
        name=project.name, 
        description=project.description, 
        technologies=project.technologies
    )
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
            body { font-family: sans-serif; margin: 40px; background-color: #f8f9fa; }
            .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .section { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
            .badge { 
                display: inline-block; 
                padding: 5px 12px; 
                margin: 5px; 
                background-color: #007bff; 
                color: white; 
                border-radius: 20px; 
                font-size: 0.9em;
                cursor: pointer; 
                transition: background 0.2s;
            }
            .badge:hover { background-color: #0056b3; }
            #suggestions { margin-top: 20px; min-height: 50px; }
            input, textarea { padding: 12px; width: 100%; font-size: 16px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { padding: 12px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background-color: #218838; }
            h1, h2 { color: #333; }
            .info { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FalkorDB + Postgres POC</h1>

            <!-- Form to Create Project -->
            <div class="section">
                <h2>1. Add New Project</h2>
                <input type="text" id="newProjectName" placeholder="Project Name (e.g., My AI App)">
                <textarea id="newProjectDesc" placeholder="Description..." rows="2"></textarea>
                <input type="text" id="newProjectTechs" placeholder="Technologies (comma separated: Python, AI, React)">
                <button onclick="createProject()">Save Project</button>
                <div id="createStatus" style="margin-top:10px;"></div>
            </div>
            
            <!-- Search / Suggestion Section -->
            <div class="section" style="border-bottom: none;">
                <h2>2. Search & Recommendations</h2>
                <p class="info">Type a project name to see suggested technologies from FalkorDB:</p>
                <input type="text" id="projectName" placeholder="Search projects..." onkeyup="getSuggestions()">
                
                <div id="suggestions"></div>
            </div>
        </div>

        <script>
            async function createProject() {
                const name = document.getElementById('newProjectName').value;
                const description = document.getElementById('newProjectDesc').value;
                const techsString = document.getElementById('newProjectTechs').value;
                const statusDiv = document.getElementById('createStatus');

                if (!name) {
                    alert("Please enter a project name");
                    return;
                }

                const technologies = techsString.split(',').map(t => t.trim()).filter(t => t !== "");

                statusDiv.innerText = "Saving...";
                
                try {
                    const response = await fetch('/projects', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, description, technologies })
                    });
                    
                    if (response.ok) {
                        statusDiv.innerHTML = '<span style="color: green;">✔ Project saved in Postgres and linked in FalkorDB!</span>';
                        document.getElementById('newProjectName').value = '';
                        document.getElementById('newProjectDesc').value = '';
                        document.getElementById('newProjectTechs').value = '';
                    } else {
                        statusDiv.innerHTML = '<span style="color: red;">❌ Error saving project</span>';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '<span style="color: red;">❌ Network error</span>';
                }
            }

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
