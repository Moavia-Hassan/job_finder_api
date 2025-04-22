from fastapi import FastAPI
from mangum import Mangum

# Create a simple FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Job Finder API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/jobs")
async def get_jobs():
    return {
        "jobs": [
            {
                "id": 1,
                "title": "Software Engineer",
                "company": "Example Corp",
                "location": "New York, NY",
                "description": "Looking for a skilled software engineer..."
            }
        ]
    }

# Create handler for Vercel
handler = Mangum(app) 