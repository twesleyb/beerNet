#!/usr/bin/env python3

brewery_id = 192
URL="https://www.beeradvocate.com/beer/profile/{}/"
url = URL.format(brewery_id)
#scrapy shell $url

# init a new project:
# $ scrapy startproject myproject [project_dir]

response.css('h1').getall() # The webpage title.

response.css('div::stats_box')
