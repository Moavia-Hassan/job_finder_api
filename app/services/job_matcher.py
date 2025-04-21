import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import re
# Load environment variables

def load_json(file_path):
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def match_jobs_with_gemini():
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # Load user input and scraped jobs
    user_input = load_json("user_input.json")
    scraped_jobs = load_json("scraped_jobs.json")

    # Construct the prompt
    prompt = """
    I have the following list of job postings. Each job posting contains multiple fields like job title, company name, location, description, salary, etc. 

    User is looking for jobs that match the following preferences:
    Position: {position}
    Experience: {experience}
    Salary: {salary}
    Job Nature: {job_nature}
    Location: {location}
    Skills: {skills}

    Please find the best matching jobs based on the above user preferences. Return the result in a structured JSON format with the following fields for each matching job:
    - job_title
    - company_name
    - location
    - description
    - salary
    - job_type (e.g., full-time, part-time, contract)
    - experience_required
    - skills_required
    - apply_link

    Here is the list of job postings (each job includes its full details):

    {scraped_jobs}

    Match the jobs based on the user input and return the best matches.
    """

    # Format the prompt with user input and job details
    formatted_prompt = prompt.format(
        position=user_input.get("position", ""),
        experience=user_input.get("experience", ""),
        salary=user_input.get("salary", ""),
        job_nature=user_input.get("job_nature", ""),
        location=user_input.get("location", ""),
        skills=user_input.get("skills", ""),
        scraped_jobs=json.dumps(scraped_jobs, indent=4)
    )

    # Initialize Gemini API with API key
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
        # Send the request to the Gemini API
        response = model.generate_content(formatted_prompt)

        # Parse the JSON response
        formatted_json = re.sub(r'```json|```', '', response.text)
        return formatted_json
    
    except Exception as e:
        # Return error information
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    match_jobs_with_gemini()
