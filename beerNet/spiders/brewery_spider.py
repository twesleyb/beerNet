#!/usr/bin/env python3

import scrapy

class BrewerySpider(scrapy.Spider):
    name = "Brewery"
    start_requests = 'http://quotes.toscrape.com/page/1/',

    def parse(self, response):
