import json
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import time
import asyncio

# Import the scraper and job matcher
from app.scraper.indeed import scrape_indeed_jobs
from app.services.job_matcher import match_jobs_with_gemini

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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

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

# Form data model
class JobSearchForm(BaseModel):
    position: str
    experience: Optional[str] = ""
    salary: Optional[str] = ""
    jobNature: Optional[str] = ""
    location: str
    skills: Optional[str] = ""

# API to get status
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

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Background scraping task
async def scrape_jobs_task(position: str, location: str, experience: str, salary: str, 
                           job_nature: str, skills: str):
    try:
        scraping_status.is_scraping = True
        scraping_status.current_step = "Saving user input"
        scraping_status.progress = 5
        await asyncio.sleep(0.5)
        
        # Save user input
        user_input = {
            "position": position,
            "experience": experience,
            "salary": salary,
            "jobNature": job_nature,
            "location": location,
            "skills": skills
        }
        
        with open("user_input.json", "w", encoding="utf-8") as f:
            json.dump(user_input, f, ensure_ascii=False, indent=4)
        
        scraping_status.current_step = "Preparing to scrape jobs"
        scraping_status.progress = 15
        await asyncio.sleep(0.5)
        
        # Scrape jobs
        scraping_status.current_step = f"Scraping jobs for {position} in {location}"
        scraping_status.progress = 25
        await asyncio.sleep(0.5)
        
        jobs = scrape_indeed_jobs(position, location)
        
        # Update progress
        scraping_status.progress = 40
        scraping_status.current_step = "Processing scraped job data"
        await asyncio.sleep(0.5)
        
        scraping_status.total_jobs = len(jobs)
        scraping_status.scraped_jobs = len(jobs)
        scraping_status.progress = 60
        await asyncio.sleep(0.5)
        
        if jobs:
            scraping_status.current_step = f"Found {len(jobs)} jobs. Preparing for AI analysis..."
            scraping_status.progress = 65
            await asyncio.sleep(0.5)
            
            # Process with LLM
            scraping_status.current_step = "Processing jobs with Gemini AI"
            scraping_status.progress = 75
            await asyncio.sleep(0.5)
            
            llm_response = match_jobs_with_gemini()
            
            scraping_status.progress = 85
            scraping_status.current_step = "Parsing AI response"
            await asyncio.sleep(0.5)
            
            # Removing json files which are no longer needed
            current_file_path = os.path.abspath(__file__)
            root_dir = os.path.dirname(os.path.dirname(current_file_path))
            os.remove(os.path.join(root_dir, 'scraped_jobs.json'))
            os.remove(os.path.join(root_dir, 'user_input.json'))
            
            # Parse JSON from LLM response
            try:
                cleaned_json = llm_response.strip()
                if cleaned_json.startswith("```json"):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json[:-3]
                
                parsed_data = json.loads(cleaned_json)
                scraping_status.result = parsed_data
                scraping_status.progress = 95
                scraping_status.current_step = "Finalizing results"
                await asyncio.sleep(0.5)
                
                scraping_status.current_step = "Completed! Found matching jobs."
                scraping_status.message = "Successfully found matching jobs!"
            except json.JSONDecodeError:
                scraping_status.result = jobs  # Fallback to raw jobs if parsing fails
                scraping_status.progress = 95
                scraping_status.current_step = "Finalizing results with raw data"
                await asyncio.sleep(0.5)
                
                scraping_status.current_step = "Completed! Using raw job data (LLM parsing failed)."
                scraping_status.message = "Found jobs but couldn't process AI response. Showing raw results."
        else:
            scraping_status.progress = 90
            await asyncio.sleep(0.5)
            
            scraping_status.current_step = "Completed! No jobs found."
            scraping_status.message = "No jobs found matching your criteria."
            
        scraping_status.progress = 100
        
    except Exception as e:
        scraping_status.error = str(e)
        scraping_status.current_step = "Error occurred"
        scraping_status.message = f"An error occurred: {str(e)}"
    finally:
        scraping_status.is_scraping = False

@app.post("/api/search")
async def search_jobs(background_tasks: BackgroundTasks, position: str = Form(...), 
                      location: str = Form(...), experience: str = Form(""), 
                      salary: str = Form(""), jobNature: str = Form(""), 
                      skills: str = Form("")):
    
    # Reset status
    scraping_status.__init__()
    
    # Validate required fields
    if not position or not location:
        return JSONResponse(
            status_code=400,
            content={"error": "Position and location are required fields"}
        )
    
    # Start background task
    background_tasks.add_task(
        scrape_jobs_task, 
        position, 
        location, 
        experience, 
        salary, 
        jobNature, 
        skills
    )
    
    return {"message": "Job search started", "status": "processing"}

@app.get("/api/results")
async def get_results():
    if scraping_status.error:
        return JSONResponse(
            status_code=500,
            content={"error": scraping_status.error}
        )
    
    return scraping_status.result

if __name__ == "__main__":
    uvicorn.run("app.integrated_api:app", host="127.0.0.1", port=8000, reload=True) 