#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_beers(brewery_id):
    """
    Collect summary beer data for a given brewery on beeradvocate.com.
    """
    BASE_URL = "https://www.beeradvocate.com/beer/profile/{}/?view=beers&show=all"
    # Parse the webpage.
    url = BASE_URL.format(brewery_id)
    session = requests.session()
    page = session.get(url)
    response = page.status_code 
    soup = BeautifulSoup(page.content,"lxml")
    # Brewery name.
    brewery = soup.find('h1').text
    # We are interested in the third table... how to avoid hard coding?
    table = soup.find_all('table')[2]
    table_rows = table.find_all('tr') # tr = table rows
    # Remove rows that don't contain any data.
    table_rows = [r for r in table_rows if len(r.find_all('td')) is not 0]
    # Collect the table data in a list.
    beer_data = list()
    for row in table_rows:
        brewery_id = row.find("a").get('href').split('/')[3] # brewery and beer id.
        beer_id = row.find("a").get('href').split('/')[4] # brewery and beer id.
        row_data = row.find_all('td') # td = table data
        row = [i.text for i in row_data]
        row.append(brewery_id)
        row.append(beer_id)
        beer_data.append(row)
    # Collect other brewery info.
    #brewery_info = soup.find("div", {"id": "info_box"}).text.split('\n')
    brewery_info = soup.find("div", {"id": "info_box"}).text
    brewery_info = brewery_info.replace("\n"," ").lstrip()
    # Create a df by combining beer info, with brewery and other brewery info.
    df_a = pd.DataFrame(beer_data)
    df_a.columns = ['Beer','Style','ABV', 'Ratings','Average',
            'Empty','Brewery_ID', 'Beer_ID']
    df_b = pd.DataFrame({"Brewery":brewery},index=range(len(df_a)))
    df_c = pd.DataFrame({"Additional Information":brewery_info},index=range(len(df_a)))
    df_d = pd.concat([df_a,df_b,df_c],axis=1)
    return(df_d)
# Ends function.
