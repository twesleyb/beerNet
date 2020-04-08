#!/usr/bin/env python3

from sys import stderr
import requests
from bs4 import BeautifulSoup
import pandas as pd
from progressbar import ProgressBar

#--------------------------------------------------------------------
## Find maximum brewery ID.
#--------------------------------------------------------------------
# The Beer advocate website is organized by brewery/beer. Unique
# integers are assigned to each brewery and beer as identifiers. 
# First, lets find out how many breweries there are on 
# beeradvocate.com--the maximum brewery ID. We will then visit each
# breweries profile page and collect their beer's data.

# FIXME: This won't really work. While loops stops when it hits a 404 webpage
# not found, but there are randomlly missing webpages...

def max_brewery_id(brewery_id=58310):
    """ Find the maximum brewery id on beeradvocate.com.
    Description:
    The Beer Advocate (BA) website contains information about different beers from
    breweries around the world. The website is organized by Brewery/Beer in 
    the following format: 
    https://www.beeradvocate.com/beer/profile/{brewery_id}/{beer_id}.
    As of 01/02/2020, there were 58,310 unique brewery IDs on 
    beeradvocate.com. Note that not all of these webpages are valid--
    there are not 58,310 breweries on BA.
    Arguments:
        brewery_id: int - brewery id to start searching from.
    """

    BASE_URL = "https://www.beeradvocate.com/beer/profile/{}/"
    response = None
    session = requests.session()

    while response != 404:
        url = BASE_URL.format(brewery_id)
        page = session.get(url)
        response = page.status_code 
        if response == 200:
            brewery_id += 1
        # Loop stops upon error, subtract one to get last valid brewery.
        max_id = brewery_id - 1
        return max_id 
    # Ends function.

# Check how many breweries there are on ba.
#max_id = max_brewery_id()
#print("There are {} breweries on Beer Advocate!".format(max_id))

#--------------------------------------------------------------------
## Get beer data for a given brewery.
#--------------------------------------------------------------------

# Could simplify to brewery summary data only + beer ids.

brewery_id = 1567

def scrape_beers(brewery_id):
    """
    Collect beer summary data from a given brewery on Beer Advocate.
    Arguments:
        brewery_id: int - brewery id.
    """

    # Request webpage.
    BASE_URL = "https://www.beeradvocate.com/beer/profile/{}/?view=beers&show=all"
    url = BASE_URL.format(brewery_id)
    session = requests.session()
    page = session.get(url)
    response = page.status_code 

    # Check if page exists.
    if response == 404:
        msg = 'Error, no profile for brewery ID: {}.'
        #print(msg.format(brewery_id), file=stderr)
        return None

    # Parse the webpage.
    soup = BeautifulSoup(page.content,"lxml")
    # Get brewery name.
    brewery = soup.find('h1').text

    # Check that beer data table exists.
    if len(soup.find_all('table')) < 3:
        msg = 'Error, "{}" does not have any beers on Beer Advocate.'
        #print(msg.format(brewery), file=stderr)
        return None

    # Parse beer data table.
    table = soup.find_all('table')[2] # we are interested in third data table.
    table_rows = table.find_all('tr') # tr = table rows
    table_rows = [r for r in table_rows if len(r.find_all('td')) is not 0] # remove empty rows. 
    beer_data = list()
    for row in table_rows:
        brewery_id = row.find("a").get('href').split('/')[3] # brewery and beer id.
        beer_id = row.find("a").get('href').split('/')[4] # brewery and beer id.
        row_data = row.find_all('td') # td = table data
        row = [i.text for i in row_data]
        row.insert(-1,brewery_id)
        row.insert(-1,beer_id)
        beer_data.append(row)

    # Collect other brewery info.
    # Need to improve scraping of address... variable street/state/country info. 
    brewery_info = soup.find("div", {"id": "info_box"})

    city = brewery_info.find_all('a')[0].text # City

    #country = brewery_info.find_all('a')[1].text # Country/State

    #country = brewery_info.find_all('a')[2].text
    #website = brewery_info.find_all('a')[3].text # Website.
    notes = brewery_info.text.replace("\n"," ").split("Notes:")[1].strip() # Brewery notes.
    other_info = [br.next_element for br in brewery_info.find_all('br')]
    address = other_info[1].split("\n")[1]

    #phone = other_info[5].split("|")[0].strip()
    additional_info = {"Address" : address, "City": city , 
            "Country" : country, "Other Notes" : notes}
    # Create a df by combining beer info, brewery name, and other info
    df_a = pd.DataFrame(beer_data)
    df_a.columns = ['Beer','Style','ABV', 'Number of Ratings','Average Rating',
            'Brewery ID', 'Beer ID','Empty']
    df_b = pd.DataFrame({"Brewery":brewery},index=range(len(df_a)))
    # Other info.
    df_c = pd.DataFrame(additional_info, index=range(len(df_a)))
    df_d = pd.concat([df_a,df_b,df_c],axis=1)
    # Reorganize columns.
    cols = ['Beer','Beer ID', 'Brewery', 'Brewery ID', 'Style','ABV',
            'Average Rating', 'Number of Ratings','Address','City',
            'Country','Other Notes']
    df = df_d[cols] 
    return(df)
# Ends function.

# Loop to scrape beer data for all breweries.
pbar = ProgressBar()
max_id = 58310
ba_data = list()
for brewery_id in pbar(range(max_id+1)):
    ba_data.append(scrape_beers(brewery_id))

# Drop empty (NoneType) entries from list and combine into single df.
ba_data = [df for df in ba_data if df is not None]
all_data = pd.concat(ba_data)

# Status resport.
nbreweries = len(ba_data)
nbeers = len(all_data)
msg = "Collected summary data for {} beers from {} breweries on Beer Advocate."
print(msg.format(nbeers,nbreweries))

# Write to csv.
all_data.to_csv("ba_beer_summary.csv")

exit()

#---------------------------------------------------------------------
## Scrape beer reviews.
#---------------------------------------------------------------------
# Loops, if statements, yup this is messy...

# Problematic, no reviews only ratings.
brewery_id = 118
beer_id = 118329
df = scrape_beer_reviews(brewery_id, beer_id)

# PBR
brewery_id = 447
beer_id = 1331

# Works?
brewery_id = 31724
beer_id = 328053
df = scrape_beer_reviews(brewery_id, beer_id)
df.to_csv('temp.csv')

# Trick to get text from last element.
def get_last_element_text(soup,tag):
    last_div = None
    for last_div in soup.find_all(tag):
        pass
    if last_div:
        text = last_div.getText()
    return text

def scrape_beer_reviews(brewery_id, beer_id):
    """
    Arguments:
        brewery_id: int - brewery id.
        beer_id: int - beer id.
    """

    BASE_URL = "https://www.beeradvocate.com/beer/profile/{}/{}"
    # Check if page exists.
    url = BASE_URL.format(brewery_id,beer_id)
    session = requests.session()
    page = session.get(url)
    response = page.status_code 

    if response == 404:
        msg = 'Error, no profile found for Beer ID: {}.'
        print(msg.format(beer_id), file=stderr)
        return None
    # Parse the webpage.
    soup = BeautifulSoup(page.content,"lxml")
    beer = soup.find('div',attrs={"class":"titleBar"}).find('br').previous_element
    # Parse beer summary stats.
    beer_stats = soup.find_all("dd", {"class": "beerstats"})
    # Problematic stats...
    # Style ranking:
    if len(beer_stats[0].find_all('a',attrs={"class":"Tooltip"})) > 1:
        style_rank = beer_stats[0].find_all('a',attrs={"class":"Tooltip"})[1].text.split("#")[1]
    else:
        style_rank = None
    # ba score:
    if beer_stats[2].find('b') is not None:
        ba_score = beer_stats[2].find('b').text
    else:
        ba_score = None
    # Overall ba rank:
    if len(beer_stats[2].find('a').text.split("#")) > 1:
        overall_rank = beer_stats[2].find('a').text.split("#")[1]
    else:
        overall_rank = beer_stats[2].find('a').text.split("#")
    # All beer summary stats.
    stats = {
        "Beer Name" : beer,
        "Beer ID" : beer_id,
        "ABV" : beer_stats[1].text,
        "Beer Style" : beer_stats[0].find('b').text,
        "Style ID" : beer_stats[0].find('a').get('href').split("/")[3],
        "Style Rank" : style_rank, # beer_stats[0].find_all('a',attrs={"class":"Tooltip"})[1].text.split("#")[1],
        "Brewery" : beer_stats[6].text,
        "Brewery ID" : brewery_id,
        "Location" : beer_stats[7].text,
        "BA Score" : ba_score, # beer_stats[2].find('b').text, # Problem if none.
        "BA Overall Rank" : overall_rank, #beer_stats[2].find('a').text.split("#")[1],
        "Average Rating" : beer_stats[3].find('b').text,
        "Percent Deviation" : beer_stats[3].text.split(":")[1].lstrip().replace("%",""),
        "Number of Reviews"  : beer_stats[4].text,
        "Number of Rankings" : beer_stats[5].text
        }
# Problem with beers that don't have any reviews, just ratings!
    # Loop to collect review data: username, user_id, normalized score, 
    # beer ratings (look, smell, taste, feel, overall), description, 
    # and review date.
    # Empty df.
    #df_b = pd.DataFrame(review_data)
    #df_b.columns = ['Look','Smell','Taste','Feel','Overall','Average Score',
    #        'Reviewer Username','Reviewer ID','Description','Review Date']
    reviews = soup.find_all("div", {"id": "rating_fullview_container"})
    review_data = list()
    for review in reviews:
        user_id = review.get('ba-user')
        username = review.find("a",{"class" : "username"}).get('href').split('/')[3]
        username = username.split(".")[0]
        norm_score = review.find('span', attrs={'class':'BAscore_norm'}).text
        ratings = review.find('span', attrs={'class':'muted'}).text.split(" | ")
        # Split ratings...
        look = ratings[0].split(":")[1]
        smell = ratings[1].split(":")[1]
        taste = ratings[2].split(":")[1]
        feel = ratings[3].split(":")[1]
        overall = ratings[4].split(":")[1]
        # Not sure of a better way to extract the user's description...
        description = review.find('span',
                attrs={'class':'muted'}).next_sibling.next_sibling.next_sibling
        # Get review date.
        review_date = get_last_element_text(review,'a')
        # Combine review data.
        review_data.append([look,smell,taste,feel,overall,
            norm_score,username,user_id,description,review_date])
        # Ends loop.
    # Create a df with beer summary stats.
    df_a = pd.DataFrame(stats,index=range(len(review_data)))
    # Create a df with beer review data.
    df_b = pd.DataFrame(review_data)
    df_b.columns = ['Look','Smell','Taste','Feel','Overall','Average Score',
            'Reviewer Username','Reviewer ID','Description','Review Date']
    # Combine dfs.
    df_c = pd.concat([df_a,df_b],axis=1)
    # Return data.
    return(df_c)
# Ends function.
