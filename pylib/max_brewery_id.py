#!/usr/bin/env python3
"""
A function to find the maximum brewery ID on beeradvocate.com.
Brewery IDs are just integers of increasing value.
The function simply starts searching at a given number, and continues
until it hits an error.
"""

import requests

def max_brewery_id(brewery_id=58310):
    """ Find the maximum brewery id on beeradvocate.com.
    Description:
    The Beer Advocate website contains information about different beers from
    breweries around the world. The website is organized by Brewery/Beer in 
    the following format: 
    https://www.beeradvocate.com/beer/profile/{brewery_id}/{beer_id}.
    As of 01/02/2020, there were 58,310 breweries on beeradvocate.com.
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
        elif response == 404:
            brewery_id -= 1
        return brewery_id
