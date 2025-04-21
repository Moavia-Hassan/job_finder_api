# Job Finder - AI-Powered Job Search

An integrated web application for searching, scraping, and analyzing job listings using AI.

## Features

- User-friendly web interface for job search
- Real-time progress tracking for job scraping
- AI-powered job matching with your preferences
- Clean, modern UI with responsive design

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your environment variables in `.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Access the web interface at http://localhost:8000

## Components

- **Web Interface**: Modern, responsive interface built with Bootstrap
- **Job Scraper**: Scrapes job listings from Indeed
- **AI Processor**: Uses Google's Gemini AI to analyze and match jobs with user preferences
- **API**: FastAPI backend for handling requests, status tracking, and serving results

## Technology Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI**: Google Gemini AI
- **Scraping**: Selenium, BeautifulSoup, DrissionPage

## API Endpoints

- `GET /`: Home page with job search form
- `POST /api/search`: Start a job search with the provided criteria
- `GET /api/status`: Check the status of the current job search
- `GET /api/results`: Get the results of the completed job search

## Required Fields

- **Position**: The job position you're looking for
- **Location**: The geographical location for the job search

## Optional Fields

- **Experience**: Years of experience
- **Salary**: Expected salary
- **Job Nature**: Remote, On-site, or Hybrid
- **Skills**: Comma-separated list of skills

## Available Endpoints

- `GET /`: Welcome message
- `GET /jobs`: Get all job listings
- `GET /jobs/{job_id}`: Get a specific job by ID
- `GET /search`: Search jobs with filters
  - Query parameters:
    - `keyword`: Search in job title and description
    - `company`: Filter by company name
    - `location`: Filter by job location
    - `job_type`: Filter by job type
- `GET /stats`: Get job statistics

## Examples

### Get all jobs
```
GET http://localhost:8000/jobs
```

### Get job by ID
```
GET http://localhost:8000/jobs/1
```

### Search jobs
```
GET http://localhost:8000/search?keyword=data&location=Islamabad
```

### Get job statistics
```
GET http://localhost:8000/stats
``` 