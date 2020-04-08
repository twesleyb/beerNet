#!/usr/bin/env python3

from sys import stderr
import requests
from bs4 import BeautifulSoup
import pandas as pd

#---------------------------------------------------------------------
## Scrape beer reviews.
#---------------------------------------------------------------------

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
    stats = {
        "Beer Name" : beer,
        "Beer Style" : beer_stats[0].find('b').text,
        "Style ID" : beer_stats[0].find('a').get('href').split("/")[3],
        "Style Rank" : beer_stats[0].find_all('a',attrs={"class":"Tooltip"})[1].text.split("#")[1],
        "ABV" : beer_stats[1].text,
        "BA Score" : beer_stats[2].find('b').text,
        "Overall Rank" : beer_stats[2].find('a').text.split("#")[1],
        "Average Rating" : beer_stats[3].find('b').text,
        "Percent Deviation" : beer_stats[3].text.split(":")[1].lstrip().replace("%",""),
        "Number of Reviews"  : beer_stats[4].text,
        "Number of Rankings" : beer_stats[5].text,
        "Brewery" : beer_stats[6].text,
        "Location" : beer_stats[7].text
        }
    # Loop to collect review data: username, user_id, normalized score, 
    # beer ratings (look, smell, taste, feel, overall), description, 
    # and review date.
    reviews = soup.find_all("div", {"id": "rating_fullview_container"})
    review_data = list()
    for review in reviews:
        user_id = review.get('ba-user')
        username = review.find("a",{"class" : "username"}).get('href').split('/')[3]
        norm_score = review.find('span', attrs={'class':'BAscore_norm'}).text
        ratings = review.find('span', attrs={'class':'muted'}).text.split(" | ")
        # Not sure of a better way to extract the user's description...
        description = review.find('span',
                attrs={'class':'muted'}).next_sibling.next_sibling.next_sibling
        # Trick to get text from last 'a' element.
        last_div = None
        for last_div in review.find_all('a'):
            pass
        if last_div:
            review_date = last_div.getText()
            # Combine review data.
            review_data.append([beer_id, brewery_id, username,
                user_id,norm_score,ratings, description,
                review_date])
        # Ends loop.
    # Create a df with beer summary stats.
    df_a = pd.DataFrame(stats,index=range(len(review_data)))
    # Create a df with beer review data.
    df_b = pd.DataFrame(review_data)
    df_b.columns = ['Beer ID','Brewery ID','Reviewer Username',
            'Reviewer ID','Average','Ratings','Description','Review Date']
    # Combine dfs.
    df_c = pd.concat([df_a,df_b],axis=1)
    # Return data.
    return(df_c)
# Ends function.
