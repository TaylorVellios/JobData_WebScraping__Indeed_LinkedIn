import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
from geopy.geocoders import Nominatim
import os

#--------------------------------------------------------------------------
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
        if job_id in jobs_parsed['Job ID']:
            break
        else:
            jobs_parsed['Employer'].append(outputs[1])
            jobs_parsed['Title'].append(outputs[0])
            jobs_parsed['City'].append(outputs[2])
            jobs_parsed['Job ID'].append(job_id)
            jobs_parsed['Time Posted'].append(time_posted)


#main function to hit indeed.com servers and begin the parsing process
def indeed_scrape(list_of_cities, search_term):
    page_num = 0

    indeed_captcha_count = 0
    for location in list_of_cities:
        print(f"------------Searching {location.replace('%2C+',', ')}:")
        for i in range(page_range):
            url = f'https://www.indeed.com/jobs?q={search_term}&l={location}&sort=date&start={page_num}'
            time.sleep(30)
        
            try:
                website = requests.get(url)
                soup = BeautifulSoup(website.content, 'html.parser')
                filtered = soup.find(id='resultsCol')
    
                job_listings = filtered.find_all(class_='jobsearch-SerpJobCard unifiedRow row result')
                
                cache_page(job_listings)

                page_num += 10
                print(f'Page {i+1}/{page_range}: Good!')
            except:
                indeed_captcha_count += 1
                print(f'Page {i+1}/{page_range}: Bad!')
                break
            finally:
                if indeed_captcha_count > 10:
                    print('Service from Indeed.com has been terminated.\nCheck your browser for a captcha prompt and try again in an hour.\n')
                    break


def clean_indeed_cities(web_scrape_results_dataframe):
    city_names = []
    for index, row in web_scrape_results_dataframe.iterrows():
        x = row['City'].split()
        try:
            if len(x[1])==2:
                city_names.append(' '.join(x[:2]))
            else:
                city_names.append(' '.join(x[:3]))
        except:
            city_names.append(float('NaN'))
    return city_names


def get_coordinates(dataframe):
    print('---------Searching For Coordinates-----------')
    geolocator = Nominatim(user_agent='my_user_agent')

    coordinates = {
        'city': [],
        'lats': [],
        'lons': []
    }

    unique_cities = set(list(dataframe['City']))

    worked_cities = []
    for i,j in enumerate(unique_cities):
        if j not in worked_cities:
            print(f"Getting Coordinates For Jobs in {j}")
        x = geolocator.geocode(j)
        coordinates['city'].append(j)
        coordinates['lats'].append(x.latitude)
        coordinates['lons'].append(x.longitude)


    lat_expand = []
    lon_expand = []

    for index, row in dataframe.iterrows():
        pointer = coordinates['city'].index(row['City'])
        lat_expand.append(coordinates['lats'][pointer])
        lon_expand.append(coordinates['lons'][pointer])
    return lat_expand, lon_expand

#Get Outputs for Terminal When Done
def get_details(dataframe):
    job_count = len(dataframe['Job ID'].unique())
    city_count = len(dataframe['City'].unique())
    city_with_most = dataframe['City'].loc[(dataframe['CityCount']==dataframe['CityCount'].max())].unique()[0]
    return job_count, city_count, city_with_most

def make_file_path(search_term):
    search = '_'.join([i.capitalize() for i in search_term])
    get_date = str(datetime.now()).split()[0]

    return f"{get_date}_{search}.csv"


#---Main Script---------------------------------------------------------------------------
pd.set_option("display.max_rows", None, "display.max_columns", None)

cities_df = pd.read_csv('CityData_Clean.csv')


print('\n----------------------------------------------------')
print(cities_df[['City','State']])
print()
city_limit = input('Enter the Index or Slice of the City/Cities Column to Search for Job Data:\n')
print()
searching = str(input("Enter the Job Title to Search For:\n"))
print()

search_term = '+'.join([i for i in searching.split()])
city_list = [row['City'] +'%2C+'+ row['State'] for index, row in cities_df.iterrows()]

#Global Var
page_range = 8  #change this number to search over more or less pages per city on indeed.com
jobs_parsed = {
    'Employer':[],
    'Title':[],
    'City':[],
    'Job ID':[], 
    'Time Posted':[],
}

total_cities = index_or_slice(city_limit,city_list)

indeed_scrape(total_cities, search_term)
print('\n\n')

#Clean City Names from Indeed Listings Along With any Weird Stuff
results_df = pd.DataFrame(jobs_parsed)
results_df['City'] = clean_indeed_cities(results_df)
results_df = results_df.dropna()

#add coordinates for all cities
coords = get_coordinates(results_df)
results_df['Lat'] = coords[0]
results_df['Lng'] = coords[1]
results_df['CityCount'] = results_df.groupby(['City'])['City'].transform('count')
print('\n\n')

#Save to File
path_str = make_file_path(search_term)
try:
    os.mkdir('Indeed_Data')
    results_df.to_csv(f'Indeed_Data/{path_str}', index=False)
except:
    results_df.to_csv(f'Indeed_Data/{path_str}', index=False)

print(results_df)
print('\n\n')

stats = get_details(results_df)
print(f"Total Jobs: {stats[0]}\n"
    f"Total Cities: {stats[1]}\n"
    f"City With the Most Results: {stats[2]}\n\n")

print(f'DataFrame Saved as {path_str}')