from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import os
import time

def initialize_driver():
    driver = webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.headless = False  # Change to True if you don't want the browser window to open
    driver = webdriver.Chrome(options=options)
    driver.wait = WebDriverWait(driver, 10)
    return driver

def login_to_linkedin(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    username_field = driver.wait.until(EC.presence_of_element_located((By.ID, "username")))
    password_field = driver.wait.until(EC.presence_of_element_located((By.ID, "password")))
    
    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

def scrape_job_details(driver, job_link):
    # Construct the full URL
    full_url = f"https://www.linkedin.com{job_link}"
    # Navigate to the job link
    driver.get(full_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_postings = soup.find_all('div', class_='job-view-layout jobs-details')
    
    for job in job_postings:
        # Extract the title using the correct class names
        title_element = job.find('h1', class_='t-24 t-bold job-details-jobs-unified-top-card__job-title')
        title = title_element.get_text(strip=True) if title_element else 'No Title Found'

        print(f"Title: {title}")
    time.sleep(2)  # Adjust based on your needs

def search_jobs(driver):
        driver.get(f"https://www.linkedin.com/jobs/search/?keywords={'Sustainability'}&location={'United States'}")

def scroll_job_list(driver):
    job_list_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'jobs-search-results-list'))
    )

    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", job_list_container
    )
    
    # Define the scroll increment (smaller value for slower scroll)
    scroll_increment = 80

    while True:
        # Scroll down by a small increment
        driver.execute_script(
            f"arguments[0].scrollTo(0, arguments[0].scrollTop + {scroll_increment});", job_list_container
        )
        
        # Wait a bit for the page to load
        time.sleep(1)  # Adjust the sleep time to control the scroll speed

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", job_list_container
        )
        
        # Check if we've reached the bottom of the job list container
        if driver.execute_script("return arguments[0].scrollTop + arguments[0].clientHeight", job_list_container) >= new_height:
            break

        # Update last_height if needed (may not be necessary with small increments)
        last_height = new_height


# Use this function in your scrape_jobs function to scroll within the job listing

def scrape_jobs(driver, max_pages):
    current_page = 1
    while current_page <= max_pages:
        scroll_job_list(driver)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_postings = soup.find_all('div', class_='job-card-container')
        
        job_links = []
        for job in job_postings:
            job_link_element = job.find('a', class_='job-card-list__title')
            job_link = job_link_element['href'] if job_link_element and job_link_element.has_attr('href') else None
            if job_link:
                job_links.append(job_link)

        # For each job link, scrape job details
        for job_link in job_links:
            scrape_job_details(driver, job_link)
            
        driver.back()  # Go back to the job list page after scraping each job detail
        scroll_job_list(driver)  # Ensure we're back at the bottom of the job list

        # Attempt to navigate to the next page
        try:
            pagination_controls = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-pagination__pages'))
            )
            next_page_buttons = pagination_controls.find_elements(By.TAG_NAME, 'button')
            next_page_button = next_page_buttons[-1]  # Typically, the last button is for navigating to the next page
            if next_page_button:
                driver.execute_script("arguments[0].click();", next_page_button)  # Use JS to click in case of overlay issues
                current_page += 1
                time.sleep(2)  # Wait for the page to load
            else:
                print("Reached the last page or next page button not found.")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

        time.sleep(2)  # Additional wait if needed
        
def main():
    driver = initialize_driver()
    try:
        login_to_linkedin(driver, 'princenoworkhere@gmail.com', 'DataClinic')
        search_jobs(driver)
        scrape_jobs(driver, 2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
