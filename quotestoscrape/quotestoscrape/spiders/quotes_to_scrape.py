# -*- coding: utf-8 -*-
from getpass import getpass
from urllib.parse import urljoin

from scrapy import FormRequest, Spider, Request


class QuotesToScrapeSpider(Spider):
    name = 'quotes_to_scrape'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def __init__(self):
        self.username = input("Enter username: ")
        self.password = getpass("Enter password: ")

    def parse(self, response):
        login_link = "http://quotes.toscrape.com/login"
        yield Request(login_link, callback=self.login, meta={'login_link': login_link})

    def login(self, response):
        print("trying to login...")
        login_link = response.meta['login_link']
        csrf_token = response.xpath('//*[@name="csrf_token"]/@value').extract_first()
        param_data = {'csrf_token': csrf_token, 'username': self.username, 'password': self.password}
        yield FormRequest(login_link, formdata=param_data, callback=self.get_authors)

    def get_authors(self, response):
        print("log in successful")
        authors = response.xpath('//*[@class="quote"]/span/small[@class="author"]')
        for author in authors:
            author_about_page_link = author.xpath('./following-sibling::a[1]/@href').extract_first()
            author_about_page_link = urljoin(self.start_urls[0], author_about_page_link)
            print("Fetching author: ", author.xpath('./text()').extract_first())
            yield Request(author_about_page_link, callback=self.get_details)

    def get_details(self, response):
        author_name = response.xpath('//*[@class="author-title"]/text()').extract_first().strip()
        birthday = response.xpath('//*[@class="author-born-date"]/text()').extract_first().strip()
        birthplace = response.xpath('//*[@class="author-born-location"]/text()').extract_first().strip().replace('in ',
                                                                                                                 '')
        yield {
            "Author name": author_name,
            "Birthday": birthday,
            "Birthplace": birthplace
        }
