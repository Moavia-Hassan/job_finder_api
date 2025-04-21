# Job Finder Application Documentation

## Project Overview

I developed Job Finder as a comprehensive solution to address the challenges job seekers face when searching for employment opportunities. The application combines web scraping technology with AI-powered job matching to create a seamless experience for users looking to find relevant positions matching their skills and preferences.

![Job Finder Homepage Screenshot - Add your screenshot here](/screenshots/1_job_finder_home_page.png)

## Working Overview



I designed and implemented Job Finder to address these challenges through:

1. **Centralized Search Interface**: I created a clean, intuitive web interface that allows users to search for jobs with specific criteria
2. **Real-time Scraping**: I built a robust scraping engine that collects up-to-date job listings from Indeed
3. **AI-Powered Matching**: I integrated Google's Gemini AI to analyze job listings against user preferences
4. **Progress Tracking**: I implemented a real-time progress system to keep users informed during the search process

## Technical Architecture

### System Architecture

I designed the application with a clear separation of concerns:

```
Job Finder
├── Frontend (HTML/CSS/JS + Bootstrap)
├── Backend API (FastAPI)
├── Job Scraper Module
│   └── Indeed Scraper with Cloudflare Bypass
├── AI Processing
│   └── Gemini AI Integration
└── Data Storage (JSON)
```
```
C:.
│   .env
│   documentation.md
│   main.py
│   ML Engineer - TA.pdf
│   README.md
│   requirements.txt
│
├───app
│   │   integrated_api.py
│   │
│   ├───scraper
│   │   │   CloudflareBypasser.py
│   │   │   indeed.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           CloudflareBypasser.cpython-313.pyc
│   │           CloudflareBypasser.cpython-39.pyc 
│   │           indeed.cpython-313.pyc
│   │           indeed.cpython-39.pyc
│   │           __init__.cpython-313.pyc
│   │           __init__.cpython-39.pyc
│   │
│   ├───services
│   │   │   job_matcher.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           job_matcher.cpython-313.pyc
│   │           job_matcher.cpython-39.pyc
│   │           __init__.cpython-313.pyc
│   │           __init__.cpython-39.pyc
│   │
│   ├───static
│   │   ├───css
│   │   │       styles.css
│   │   │
│   │   └───js
│   │           main.js
│   │
│   ├───templates
│   │       index.html
│   │
│   ├───utils
│   └───__pycache__
│           api.cpython-313.pyc
│           integrated_api.cpython-313.pyc
│           integrated_api.cpython-39.pyc
│           main.cpython-313.pyc
│           main.cpython-39.pyc
│           __init__.cpython-39.pyc
│
├───screenshots
│       1_job_finder_home_page.png
```

### Technology Stack

I carefully selected technologies based on their performance, reliability, and suitability for the task:

- **Backend**: 
  - FastAPI (Python web framework for building APIs)
  - Uvicorn (ASGI server)
  - Python 3.9+
  
- **Frontend**: 
  - HTML5/CSS3/JavaScript
  - Bootstrap 5 (for responsive design)
  - Fetch API (for AJAX requests)
  
- **Web Scraping**:
  - Selenium (for browser automation)
  - BeautifulSoup (for HTML parsing)
  - DrissionPage (for Cloudflare bypass)
  
- **AI/Machine Learning**:
  - Google Generative AI (Gemini 2.0 Flash model)
  
- **Other Tools**:
  - Python-dotenv (for environment variable management)

## Implementation Details



### AI Job Matching

For the AI-powered job matching, I integrated Google's Gemini API:

1. I designed a structured prompt that clearly defines the matching criteria
2. I implemented error handling for various API response formats
3. I ensured the system could fall back to raw job data if AI processing failed

The core of my AI integration was the carefully crafted prompt engineering:

```python
prompt = """
I have the following list of job postings. Each job posting contains multiple fields like job title, company name, location, description, salary, etc. 

User is looking for jobs that match the following preferences:
Position: {position}
Experience: {experience}
Salary: {salary}
Job Nature: {job_nature}
Location: {location}
Skills: {skills}

Please find the best matching jobs based on the above user preferences...
"""
```

![AI Matching Results - Add your screenshot here](/screenshots/2_ai_matched_results.png)

### Asynchronous Processing

I implemented an asynchronous processing architecture to maintain a responsive user interface during the potentially time-consuming scraping and AI analysis:

1. I used FastAPI's BackgroundTasks for handling long-running operations
2. I created a status tracking system with granular progress updates
3. I implemented proper exception handling with user-friendly error messages

```python
@app.post("/api/search")
async def search_jobs(background_tasks: BackgroundTasks, position: str = Form(...), 
                      location: str = Form(...), ...):
    
    # Start background task
    background_tasks.add_task(
        scrape_jobs_task, 
        position, 
        location, 
        ...
    )
```

### Frontend Development

For the user interface, I focused on creating a clean, intuitive experience:

1. I designed a responsive layout using Bootstrap 5
2. I created a real-time progress tracking system with animated progress bars
3. I implemented error handling with user-friendly messages
4. I designed visually appealing job cards to display the results

A key UI component I developed was the animated progress tracking:

```javascript
function animateProgressBar(startValue, endValue) {
    const duration = 300; // milliseconds
    const startTime = performance.now();
    
    function updateProgress(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        // Calculate current value using easing function
        const currentValue = startValue + (endValue - startValue) * progress;
        
        // Update progress bar
        progressBar.style.width = `${currentValue}%`;
        progressBar.setAttribute('aria-valuenow', currentValue);
        progressPercent.textContent = `${Math.round(currentValue)}%`;
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}
```

![Progress Tracking - Add your screenshot here](/screenshots/3_progress_tracking.png)

## Challenges & Solutions

### Challenge 1: Cloudflare Protection

One of the most significant challenges I faced was bypassing Cloudflare's anti-bot protection on Indeed. I solved this by:

Found this cloudflare bypasser from Github repo after hours of research and brainstorming with my friend.

### Challenge 2: Inconsistent HTML Structure

Job listings on Indeed frequently change their HTML structure, making scraping difficult. I addressed this by:

1. Implementing multiple selector strategies with fallbacks
2. Creating robust parsing logic with error handling
3. Using more reliable data-testid attributes where available


### Challenge 3: Progress Reporting

Creating a smooth progress reporting system was challenging due to the variable time each step required. I resolved this by:

1. Adding granular progress steps throughout the scraping and AI analysis process
2. Implementing small delays to ensure frontend can capture state changes
3. Creating a smooth animation system for the progress bar

## Testing & Quality Assurance

For quality assurance, I implemented:

1. **Error Handling**: Comprehensive error handling at all levels of the application
2. **Fallback Mechanisms**: Alternative paths when primary processes fail
3. **Input Validation**: Server-side validation of user inputs
4. **Responsive Design Testing**: Testing across multiple device sizes

## Future Enhancements Remaining



1. **Multi-source Scraping**: LinkedIn and Glassdoor scraping is not implemented in this assessment due to shoratge of time and costly process.


## Running the Application

To run the Job Finder application:

1. Install dependencies: `pip install -r requirements.txt`
2. Set up the environment:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```
3. Start the server: `python main.py`
4. Access the application at http://localhost:8000


## Conclusion

Developing Job Finder was a fulfilling challenge that allowed me to combine web scraping, AI integration, and full-stack development skills. I'm particularly proud of the seamless user experience and the intelligent job matching capabilities I was able to implement.

The project demonstrates my ability to:
- Architect and implement full-stack web applications
- Integrate complex third-party APIs and services
- Create elegant solutions to technical challenges
- Design intuitive user interfaces
- Implement robust error handling and fallback mechanisms
