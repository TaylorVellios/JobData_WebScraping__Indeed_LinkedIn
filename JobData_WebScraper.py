import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import datetime
from geopy.geocoders import Nominatim
import os

#---------------------------------------------------------------------------------------------------------------------------------------------
#Function to determine user input is a single index or a slice range, returns accordingly
def index_or_slice(user_input, city_list):
    if '[' in user_input:
        user_input = user_input.replace('[','')
    if  ']' in user_input:
        user_input = user_input.replace(']','')
    try:
        index = int(user_input)
        return [city_list[index]]
    except:
        if user_input.startswith(':'):
            bye = user_input.replace(':','')
            return city_list[0:int(bye)]
        else:
            slice = user_input.split(':')
            return city_list[int(slice[0]):int(slice[-1])]


# ------------------------------------------------------------------------------------------------------------------------CACHING-LINKEDIN-----
## CACHING EACH PAGE FROM LINKEDIN PING
def cache_linkedin(linkedin_dict):


    today_check = datetime.datetime.now()
    one_month = datetime.timedelta(31)

    for i in range(len(linkedin_dict['Job ID'])):

        post_time = linkedin_dict['Time Posted'][i]
        new_time = datetime.datetime.strptime(post_time,'%Y-%m-%d')

        if linkedin_dict['Job ID'][i] in linkedin_jobs['Job ID']:
            pass
        elif new_time + one_month < today_check:
            pass
        else:
            linkedin_jobs['Employer'].append(linkedin_dict['Employer'][i])
            linkedin_jobs['Title'].append(linkedin_dict['Title'][i])
            linkedin_jobs['City'].append(linkedin_dict['City'][i])
            linkedin_jobs['Job ID'].append(linkedin_dict['Job ID'][i])
            linkedin_jobs['Time Posted'].append(linkedin_dict['Time Posted'][i])
            linkedin_jobs['Job Board'].append('LinkedIn.com')


# --------------------------------------------------------------------------------------------------------------------------CACHING-INDEED-----
#Allows each ping to indeed.com to be filtered and stored to save on RAM
def cache_page(scraped_page):

    for job in scraped_page:
#CONVERT HTML TO TEXT VIA BEAUTIFUL SOUP AND SEPARATE INTO LIST
        job_data = job.get_text().replace('\n','^^')
        job_id = job.find('a').get('id')
        
        outputs = []
        phrase = ''
        for i in job_data:
            if i != '^':
                phrase += i
            elif i == '^' and len(phrase)>1:
                outputs.append(phrase)
                phrase = ''
            else:
                phrase = ''

        if 'new' in outputs:
            outputs.remove('new')

#ignoring anything marked 30+ days ago
        time_posted = job.find(class_='date date-a11y').text
        if time_posted == '30+ days ago':
            break
            
#managing the odd order of information when pulling data
        for i in outputs:
            try:
                f = float(i)
                outputs.remove(i)
            except:
                pass
        if job_id in indeed_jobs['Job ID']:
            break
        else:
            indeed_jobs['Employer'].append(outputs[1])
            indeed_jobs['Title'].append(outputs[0])
            indeed_jobs['City'].append(outputs[2])
            indeed_jobs['Job ID'].append(job_id)
            indeed_jobs['Time Posted'].append(time_posted)
            indeed_jobs['Job Board'].append('Indeed.com')




# --------------------------------------------------------------------------------------------------------------------------SCRAPING-LINKEDIN-----
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
    city_search = location.replace(' ','%20')


    url =f"https://www.linkedin.com/jobs/search?keywords={'%20'.join(search_term.split())}&location={city_search}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum={page}"
    scraper = requests.get(url)

    soup = BeautifulSoup(scraper.content, 'html.parser')
    job_listings = soup.find_all(class_='result-card job-result-card result-card--with-hover-state')


    failed_job_count = 0
    for job_index, single_job in enumerate(job_listings):
        
        try:
            jobs['Employer'].append(single_job.find(class_="result-card__subtitle-link job-result-card__subtitle-link").text)
            jobs['Title'].append(single_job.find(class_="result-card__title job-result-card__title").text)
            jobs['City'].append(single_job.find(class_='job-result-card__location').text)
            jobs['Job ID'].append(single_job.get('data-id'))
            jobs['Job Board'].append('LinkedIn')
            
            #NEW JOB POSTINGS HAVE A DIFFERENT CLASS TO TRIGGER GREEN BOLD TEXT IN BROWSER
            try:
                jobs['Time Posted'].append(single_job.find(class_="job-result-card__listdate--new").get('datetime'))
            except:
                jobs['Time Posted'].append(single_job.find(class_="job-result-card__listdate").get('datetime'))
        except:
            failed_job_count += 1
            pass
    #NEW JOB POSTINGS HAVE A DIFFERENT CLASS TO TRIGGER GREEN BOLD TEXT IN BROWSER

    return (jobs, failed_job_count)


# ---------------------------------------------------------------------------------------------------------------------------SCRAPER-----------
#main function to hit indeed/linkedin servers and begin the parsing process
def indeed_scrape(list_of_cities, search_term):

    page_num = 0

    indeed_captcha_count = 0
    linkedin_captcha_count = 0
    city_len = len(list_of_cities)
    current=1
    for location in list_of_cities:

        text_location = location.replace('**',', ')
        indeed_location = '%20'.join(location.split()).replace('**','%2C+')
        linkedin_location = location.replace('**',' ')

        print(f"------------Searching {text_location} -- {current}/{city_len}:")
        for i in range(page_range):
            url = f'https://www.indeed.com/jobs?q={search_term}&l={indeed_location}&sort=date&start={page_num}'
            time.sleep(30)
        
            indeed_stat = True
            linkedin_stat = True
            try:
                #PING INDEED AND CACHE
                website = requests.get(url)
                soup = BeautifulSoup(website.content, 'html.parser')
                filtered = soup.find(id='resultsCol')
                job_listings = filtered.find_all(class_='jobsearch-SerpJobCard unifiedRow row result')
                cache_page(job_listings)
                page_num += 10
            except:
                indeed_captcha_count += 1
                indeed_stat = False
            finally:
                if indeed_captcha_count > 10:
                    print('Service from Indeed.com has been terminated.\nCheck your browser for a captcha prompt and try again in an hour.\n')
                    break
            

            try:
                #PING LINKEDIN AND CACHE------------------------------------------------
                linkedin_get = linkedin_scraper(linkedin_location, search_term, i)
                cache_linkedin(linkedin_get[0])
            except:
                linkedin_captcha_count += 1
                linkedin_stat = False

            indeed_print, linkedin_print = 'Good!','Good!'
            if indeed_stat == False:
                indeed_print = 'Bad!'
            if linkedin_stat == False:
                linkedin_print = 'Bad!'
            print(f'Indeed {i+1}/{page_range}: {indeed_print}    //     Linkedin {i+1}/{page_range}: {linkedin_print}  --  Jobs Rejected: {linkedin_get[1]}')

        current += 1


# ---------------------------------------------------------------------------------------------------------------------------------------------
def clean_indeed_cities(web_scrape_results_dataframe):
    city_names = []
    for index, row in web_scrape_results_dataframe.iterrows():
        city = row['City'].split()
        x = [i.replace(',','') for i in city if i.lower() not in ['metropolitan', 'area', 'metroplex', 'streets']]

        garbage_check = [x.index(i) for i in x if '(' in i]
        if len(garbage_check) == 1:
            parenth_index = garbage_check[0]
        else:
            parenth_index = None

        x = x[:parenth_index]
        for j,i in enumerate(x):
            try:
                math = int(i)
                x.remove(i)
            except:
                pass

        if len(x) == 0:
            x = ['United States', 'US']
        city_names.append(' '.join(x))
    return city_names

# ------------------------------------------------------------------------------------------------------------------COORDINATES-----------------
def get_coordinates(dataframe):
    print('---------Searching For Coordinates-----------')
    coordinates = {
        'city': [],
        'lats': [],
        'lons': []
    }

    geolocator = Nominatim(user_agent='my_user_agent')

    unique_cities = set(list(dataframe['City']))

    bad_city_count = 0
    worked_cities = []
    for i,j in enumerate(unique_cities):
        city_name = j.replace("'",'')
        if city_name not in worked_cities:

            found = True
            coordinates['city'].append(city_name)
            try:
                x = geolocator.geocode(city_name)
                coordinates['lats'].append(x.latitude)
                coordinates['lons'].append(x.longitude)
            except:
                bad_city_count += 1
                coordinates['lats'].append(float("NaN"))
                coordinates['lons'].append(float("NaN"))
                found = False
            
            if found == True:
                print(f"Coordinates OKAY: {city_name}")
            else:
                print(f"Coordinates BAD: {city_name}")
         

    lat_expand = []
    lon_expand = []

    for index, row in dataframe.iterrows():
        pointer = coordinates['city'].index(row['City'])
        lat_expand.append(coordinates['lats'][pointer])
        lon_expand.append(coordinates['lons'][pointer])
    return lat_expand, lon_expand, bad_city_count

#--------------------------------------------------------------------------------------------------------------------------Runtime-Details--
#Get Outputs for Terminal When Done
def get_details(dataframe):
    job_count = len(dataframe['Job ID'].unique())
    city_count = len(dataframe['City'].unique())
    city_with_most = dataframe['City'].loc[(dataframe['CityCount']==dataframe['CityCount'].max())].unique()[0]
    return job_count, city_count, city_with_most

def make_file_path(search_term):
    search = '_'.join([i.capitalize() for i in search_term.split('+')])
    get_date = str(datetime.datetime.now()).split()[0]

    return f"{get_date}_{search}.csv"


#------------------------------------------------------------------------------------------------------------------------------Main-Script--
pd.set_option("display.max_rows", None, "display.max_columns", None)

cities_df = pd.read_csv('CityData_Clean.csv')


print('\n----------------------------------------------------')
print(cities_df[['City','State']])
print('\n----------------------------------------------------')

print()
city_limit = input('Enter the Index or Slice of the City/Cities Column to Search for Job Data:\n')
print()
print('----------------------------------------------------\n')

searching = str(input("Enter the Job Title to Search For:\n"))
print()
print('----------------------------------------------------\n')

search_term = '+'.join([i for i in searching.split()])
city_list = [row['City'] +'**'+ row['State'] for index, row in cities_df.iterrows()]


#Global Var
page_range = 8  #change this number to search over more or less pages per city on indeed.com
indeed_jobs = {
    'Employer':[],
    'Title':[],
    'City':[],
    'Job ID':[], 
    'Time Posted':[],
    'Job Board':[]
}

linkedin_jobs = {
    'Employer':[],
    'Title':[],
    'City':[],
    'Job ID':[], 
    'Time Posted':[],
    'Job Board':[]
}


total_cities = index_or_slice(city_limit,city_list)

indeed_scrape(total_cities, search_term)
print('\n\n')

#Clean City Names from Indeed Listings Along With any Weird Stuff
indeed_job_df = pd.DataFrame(indeed_jobs)
linkedin_job_df = pd.DataFrame(linkedin_jobs)
results_df = indeed_job_df.append(linkedin_job_df, ignore_index=True)



results_df['City'] = clean_indeed_cities(results_df)
results_df = results_df.dropna()
print(f'*****DataFrame Successfully Created*****')


#add coordinates for all cities
coords = get_coordinates(results_df)
results_df['Lat'] = coords[0]
results_df['Lng'] = coords[1]
results_df['CityCount'] = results_df.groupby(['City'])['City'].transform('count')
failed_city_coords = coords[2]
print('\n\n')

#Save to File
path_str = make_file_path(search_term)
try:
    os.mkdir('Job_Data')
    results_df.to_csv(f'Job_Data/{path_str}', index=False)
except:
    results_df.to_csv(f'Job_Data/{path_str}', index=False)

print('\n\n')

stats = get_details(results_df)
print(f"Total Jobs: {stats[0]}\n"
    f"Indeed Jobs: {(results_df['Job Board']=='Indeed.com').sum()}\n"
    f"LinkedIn Jobs: {(results_df['Job Board']=='LinkedIn.com').sum()}\n"
    f"Total Cities: {stats[1]}\n"
    f"Count of Cities that Failed Coordinate Search: {failed_city_coords}\n\n")

print(f'DataFrame Saved as {path_str}')