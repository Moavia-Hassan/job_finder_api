from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import json
from pathlib import Path
import time
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Job Finder API",
    description="Web API for finding and filtering job listings",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for Vercel - adjust path if needed
static_path = Path(__file__).parent.parent / "app" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Set up templates for Vercel - adjust path if needed
templates_path = Path(__file__).parent.parent / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

# Job scraping status tracking
class ScrapingStatus:
    def __init__(self):
        self.is_scraping = False
        self.total_jobs = 0
        self.scraped_jobs = 0
        self.current_step = "Not started"
        self.progress = 0
        self.result = []
        self.message = ""
        self.error = None

scraping_status = ScrapingStatus()

# Root endpoint serving the HTML template
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if templates is not None:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse(content="<html><body><h1>Job Finder API</h1><p>Templates directory not found</p></body></html>")

# API endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/status")
async def get_status():
    return {
        "is_scraping": scraping_status.is_scraping,
        "total_jobs": scraping_status.total_jobs,
        "scraped_jobs": scraping_status.scraped_jobs,
        "current_step": scraping_status.current_step,
        "progress": scraping_status.progress,
        "message": scraping_status.message,
        "error": scraping_status.error
    }

@app.get("/api/results")
async def get_results():
    if scraping_status.error:
        return JSONResponse(
            status_code=500,
            content={"error": scraping_status.error}
        )
    
    return scraping_status.result

# Simulated job search for Vercel deployment
@app.post("/api/search")
async def search_jobs(background_tasks: BackgroundTasks, 
                      position: str = Form(...), 
                      location: str = Form(...),
                      experience: str = Form(""),
                      salary: str = Form(""),
                      jobNature: str = Form(""),
                      skills: str = Form("")):
    
    # Reset status
    scraping_status.__init__()
    
    # Start background task for simulated job search
    background_tasks.add_task(
        simulated_job_search,
        position,
        location,
        experience,
        salary,
        jobNature,
        skills
    )
    
    return {"message": "Job search started", "status": "processing"}

# Simulated job search function 
async def simulated_job_search(position, location, experience, salary, job_nature, skills):
    try:
        scraping_status.is_scraping = True
        scraping_status.current_step = "Initializing job search"
        scraping_status.progress = 5
        await asyncio.sleep(1)  # Simulate delay
        
        scraping_status.current_step = "Searching for jobs"
        scraping_status.progress = 20
        await asyncio.sleep(2)  # Simulate delay
        
        scraping_status.current_step = "Collecting job details"
        scraping_status.total_jobs = 5
        for i in range(5):
            scraping_status.scraped_jobs = i + 1
            scraping_status.progress = 20 + (i + 1) * 10
            await asyncio.sleep(1)  # Simulate delay
        
        scraping_status.current_step = "Analyzing with AI"
        scraping_status.progress = 80
        await asyncio.sleep(2)  # Simulate delay
        
        # Sample job results
        sample_jobs = [
            {
                "id": 1,
                "title": f"{position} Engineer",
                "company": "Example Corp",
                "location": location,
                "description": f"Looking for a skilled {position} engineer with {experience} experience...",
                "salary": salary or "$120,000 - $150,000",
                "job_nature": job_nature or "Remote",
                "skills_required": skills or "Python, JavaScript, SQL",
                "date_posted": "2023-05-15",
                "match_score": 95
            },
            {
                "id": 2,
                "title": f"Senior {position}",
                "company": "Tech Solutions Inc",
                "location": location,
                "description": f"Seeking experienced {position} professional with {experience} years...",
                "salary": salary or "$130,000 - $160,000",
                "job_nature": job_nature or "Hybrid",
                "skills_required": skills or "Java, AWS, Kubernetes",
                "date_posted": "2023-05-16",
                "match_score": 87
            },
            {
                "id": 3,
                "title": f"{position} Specialist",
                "company": "Innovative Systems",
                "location": location,
                "description": f"Join our team as a {position} specialist...",
                "salary": salary or "$110,000 - $140,000",
                "job_nature": job_nature or "On-site",
                "skills_required": skills or "C++, Python, Docker",
                "date_posted": "2023-05-17",
                "match_score": 82
            }
        ]
        
        scraping_status.current_step = "Completed"
        scraping_status.progress = 100
        scraping_status.result = sample_jobs
        
    except Exception as e:
        scraping_status.error = str(e)
    finally:
        scraping_status.is_scraping = False

# Create handler for Vercel
handler = Mangum(app)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)