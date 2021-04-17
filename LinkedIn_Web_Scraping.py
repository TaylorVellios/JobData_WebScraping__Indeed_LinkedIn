import requests
from bs4 import BeautifulSoup
import time



def linkedin_scraper(city_to_search, search_term, page):

    jobs = {
        'Employer':[],
        'Title':[],
        'City':[],
        'Job ID':[], 
        'Time Posted':[],
        'Job Board':[]
    }

    #makes list of job postings per page
    location = city_to_search
    city_search = '%20'.join(location.split()).replace(',','%2C')

    url =f"https://www.linkedin.com/jobs/search?keywords={'%20'.join(search_term.split())}&location={city_search}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum={page}"
    scraper = requests.get(url)

    soup = BeautifulSoup(scraper.content, 'html.parser')
    job_listings = soup.find_all(class_='result-card job-result-card result-card--with-hover-state')

    for single_job in job_listings:
        
        try:
            jobs['Employer'].append(single_job.find(class_="result-card__subtitle-link job-result-card__subtitle-link").text)
            jobs['Title'].append(single_job.find(class_="result-card__title job-result-card__title").text)
            jobs['City'].append(single_job.find(class_='job-result-card__location').text)
            jobs['Job ID'].append(single_job.get('data-id'))
            jobs['Job Board'].append('LinkedIn')
        except:
            print(f'Failed to Get LinkedIn Data')
            break
    #NEW JOB POSTINGS HAVE A DIFFERENT CLASS TO TRIGGER GREEN BOLD TEXT IN BROWSER
        try:
            jobs['Time Posted'].append(single_job.find(class_="job-result-card__listdate--new").get('datetime'))
        except:
            jobs['Time Posted'].append(single_job.find(class_="job-result-card__listdate").get('datetime'))
    return jobs

