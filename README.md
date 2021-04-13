# Indeed_Web_Scraping
Scraping Indeed (as ethically as possible) for Job Data Across Many Cities For the Younger Nomadic Workforce.


## Purpose
To compile job listing data across the US's largest cities for your career of choice.<br></br>

Millenials and Zoomers are proving that they are happy to move where the jobs are.<br></br>

This script allows the user to gain the following insights:
* Which metropolitan areas in the US have higher concentrations of recent job postings for their industry.
* The companies that post listings in those areas, allowing for an easier job search.
* Locations of employers in the nearby-surrounding cities across the area, allowing the user to see and narrow down housing location choices.


## Dependencies 
#### Indeed_WebScraping.py
* Pandas
* BeautifulSoup
* geopy

### Plotting_Indeed_Data.ipynb
* gmaps
* gmaps.config.py file with your api key set to a variable named 'g_key'

<br></br>
## Features
This repository contains a main script (Indeed_WebScraping.py) as well as a Jupyter Notebook file (Plotting_Indeed_Data.ipynb).<br></br>

The included .csv file (CityData_Clean.csv) contains the top 100 cities in the US sorted by descending population size.<br></br>


The Web Scraping python script is made to search and store only recent job postings on Indeed.com (within 30 days) and return them as a .csv file on your machine.<br></br>

### Instructions for Scraper:
* Run Indeed_WebScraping.py in bash/terminal
* You will be prompted for two inputs:
** 1. A Single Index or a One/Two Digit Slice (with colon separator) of the City/State Columns in the DataFrame displayed.
** 2. A search term for whatever job title you would like to scrape.
<br></br>

*Please note that this script is set to ping indeed.com once every 30 seconds.<br>
*By default, this script will search for 8 pages of results per city and filter out anything posted over a month ago.<br>
*tl:dr -- IT TAKES A LONG TIME, DO NOT ADJUST SLEEP TIME<br>
*Indeed.com will require a captcha if you ping it too often, breaking the program. Leave this open in an active terminal, or load it on a raspberry pi and go about your day.
<br></br>

<br></br>


### Instructions for Mapper:
* Ensure you have set your gmaps api token to a variable named "g_key" in a file named "g_config.py" in this repo's directory.
* Open Plotting_Indeed_Data.ipynb in Jupyter Notebook.
* Find your output .csv file in the new 'Indeed_Data' directory created when the scraper finished. It will be named with the current day and your search term.
* Enter the file name of that .csv in the first empty-string variable 'file_name' in the second cell.
* Run it and see where the jobs pop up!





