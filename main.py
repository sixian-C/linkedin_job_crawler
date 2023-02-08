from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import yaml
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import traceback

# Creating a webdriver instance
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
# This instance will be used to log into LinkedIn

# Read external variables form yaml file (username & password)
with open('config.yaml') as f:
    var = yaml.safe_load(f)

# Opening linkedIn's login page
driver.get("https://linkedin.com/uas/login")

# waiting for the page to load

# entering username & password
driver.find_element("xpath", '//*[@id="username"]').send_keys(var['username'])
driver.find_element("xpath", '//*[@id="password"]').send_keys(var['password'])
time.sleep(1)  # wait for one second  so the page doesn't flink

# Submiting form
driver.find_element(
    "xpath", '//*[@id="organic-div"]/form/div[3]/button').click()

# go to job page, the url here is data scientist job posting. Replace with the job you want to scrape.
driver.get("https://www.linkedin.com/jobs/search/?currentJobId=3459267979&keywords=data%20scientist&refresh=true")

# Get all links for these offers
links = []
# Navigate 13 pages
print('Links are being collected now.')
try:
    for page in range(2, 10):  # how many linkedin job pages the crawler will go through
        time.sleep(2)

        jobs_block = driver.find_element(
            By.CLASS_NAME, 'jobs-search-results-list')
        jobs_list = jobs_block.find_elements(
            "xpath", '//*[@id="main"]/div/section[1]/div/ul')

        for job in jobs_list:
            all_links = job.find_elements(By.TAG_NAME, 'a')
            for a in all_links:
                if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links:
                    links.append(a.get_attribute('href'))
                else:
                    pass
            # scroll down for each job element
            driver.execute_script("arguments[0].scrollIntoView();", job)

        print(f'Collecting the links in the page: {page-1}')
        # go to next page:
        driver.find_element(
            "xpath", f"//button[@aria-label='Page {page}']").click()
except Exception:
    traceback.print_exc()
#     pass
print('Found ' + str(len(links)) + ' links for job offers')

# Create empty lists to store information
job_titles = []
company_names = []
company_locations = []
work_methods = []
post_dates = []
work_times = []
job_desc = []

i = 0
j = 1
# Visit each link one by one to scrape the information
print('Visiting the links and collecting information just started.')
for url in links:
    print('\n')
    print(url)
    try:
        driver.get(url)
        time.sleep(4)
        # Click See more.
        # driver.find_elements(By.CLASS_NAME,"artdeco-card__actions").click()
        driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[2]/footer').click()
        time.sleep(2)
    except Exception:
        pass
        # traceback.print_exc()
    try:
        driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[4]/footer').click()
    except:
        pass
    time.sleep(2)

    # Find the general information of the job offers
    # some linkedin pages don't contain work_method and work_time information, we need to catch error and tag this info as unknwon.
    try:
        job_titles.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/h1').text)
    except Exception:
        traceback.print_exc()
        job_titles.append('unknown')
    try:
        company_names.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[1]').text)
    except Exception:
        traceback.print_exc()
        company_names.append('unknown')
    try:
        company_locations.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[2]').text)
    except Exception:
        traceback.print_exc()
        company_locations.append('unknown')
    try:
        work_methods.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[3]').text)
    except Exception:
        traceback.print_exc()
        work_methods.append('unknown')
    try:
        post_dates.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[2]/span[1]').text)
    except Exception:
        traceback.print_exc()
        post_dates.append('unknown')
    try:
        work_times.append(driver.find_element(
            "xpath", '/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[2]/ul/li[1]').text)
    except Exception:
        traceback.print_exc()
        work_times.append('unknown')

    print(f'Scraping the {j} Job General Information.')
    time.sleep(2)

    # Scraping the job description
    # The job description page might not load properly, thus causing an error, we can use try-except to catch this error and tag it
    # as no description found.
    try:
        job_description = driver.find_elements(
            By.CLASS_NAME, 'jobs-description__content')
        for description in job_description:
            job_text = description.find_element(
                By.CLASS_NAME, "jobs-box__html-content").text
            job_desc.append(job_text)
            print(f'Scraping the {j} Job Description.')
            time.sleep(2)
    except:
        traceback.print_exc()
        job_desc.append('No description found')
    j += 1

# Creating the dataframe
df = pd.DataFrame(list(zip(job_titles, company_names,
                           company_locations, work_methods,
                           post_dates, work_times, links, job_desc)),
                  columns=['job_title', 'company_name',
                           'company_location', 'work_method',
                           'post_date', 'work_time', 'job_links', 'job_desc'])

# Storing the data to csv file
df.to_csv('job_offers.csv', index=False)

# Output job descriptions to txt file
with open('job_descriptions.txt', 'w', encoding="utf-8") as f:
    for line in job_desc:
        f.write(line)
        f.write('\n')

with open('links.txt', 'w', encoding="utf-8") as f:
    for count, line in enumerate(links):
        f.write(str(count))
        f.write('\n')
        f.write(line)
        f.write('\n')
