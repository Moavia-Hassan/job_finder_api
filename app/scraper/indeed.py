import json
import time
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from .CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_single_element(driver, css_selector, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    except Exception:
        return None

def get_all_elements(driver, css_selector, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        )
    except Exception:
        return []

def click_element(element):
    try:
        element.click()
        return True
    except Exception:
        return False

def scrape_indeed_jobs(position, location):
    try:
        # Launch DrissionPage and bypass Cloudflare
        driver = ChromiumPage()
        driver.get('https://www.indeed.com/jobs/')
        cf_bypasser = CloudflareBypasser(driver)
        cf_bypasser.bypass()

        cookies_list = driver.cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}
        user_agent = driver.user_agent
        driver.quit()

        # Launch Selenium with cookies
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--headless=new')  
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')  
        options.add_argument('--disable-dev-shm-usage')
        selenium_driver = webdriver.Chrome(options=options)

        url = f"https://pk.indeed.com/jobs?q={position.replace(' ', '%20')}&l={location.replace(' ', '%20')}"
        selenium_driver.get("https://pk.indeed.com")
        time.sleep(3)

        for name, value in cookies.items():
            try:
                selenium_driver.add_cookie({'name': name, 'value': value})
            except Exception:
                pass

        selenium_driver.get(url)

        # Find job cards using a more reliable selector
        job_cards = get_all_elements(selenium_driver, "h2[data-testid='jobTitle']", timeout=5)
        if not job_cards:
            # Fallback to the old selector if the new one doesn't work
            job_cards = get_all_elements(selenium_driver, "h2[class*='jobTitle']", timeout=5)

        jobs = []

        for i, job_card in enumerate(job_cards[:10], 1):
            selenium_driver.execute_script("arguments[0].scrollIntoView();", job_card)
            clicked = click_element(job_card)
            time.sleep(3)

            desc_element = get_single_element(selenium_driver, "div.jobsearch-JobComponent", timeout=10)

            if desc_element:
                description_html = desc_element.get_attribute("outerHTML")
                description_text = desc_element.text.strip()
                soup = BeautifulSoup(description_html, 'html.parser')
                apply_link = selenium_driver.current_url
                
                job_title_tag = soup.find(attrs={"data-testid": "jobsearch-JobInfoHeader-title"})

                # Extract the job title
                job_title = 'Unknown Title'
                if job_title_tag:
                    # Remove the nested span that says "- job post", if present
                    unwanted_span = job_title_tag.find("span", string=lambda text: text and "job post" in text)
                    if unwanted_span:
                        unwanted_span.decompose()

                    # Get the cleaned job title
                    job_title = job_title_tag.get_text(strip=True)
                
                # Extract company using data-testid attribute
                company_element = soup.select_one('div[data-testid="inlineHeader-companyName"] a')
                if not company_element:
                    company_element = soup.select_one('div[data-company-name="true"] a')
                
                company_name = "Not specified"
                if company_element:
                    company_name = company_element.text.strip()
                    # Remove any nested SVG or irrelevant elements' text
                    for svg in company_element.select('svg'):
                        svg.decompose()
                    company_name = company_element.text.strip()

                job_data = {
                    "job_id": i,
                    "job_title": job_title,
                    "company": company_name,
                    "location": location,
                    "salary": next((p.text for p in soup.find_all('p') if 'Rs' in p.text or 'PKR' in p.text), "Not specified"),
                    "job_type": next((p.text for p in soup.find_all('p') if 'Job Type' in p.text), "Not specified").replace('Job Type:', '').strip(),
                    "experience_required": next((li.text for li in soup.find_all('li') if 'year' in li.text.lower()), "Not specified"),
                    "job_nature": "On-site" if 'in person' in description_text.lower() else "Not specified",
                    "apply_link": apply_link,
                    "job_description": description_text
                }

                jobs.append(job_data)

        selenium_driver.quit()
        
        with open("scraped_jobs.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)

        return jobs

    except Exception:
        return []
