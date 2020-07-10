'''
This code parses information/data from the guardian newspaper -- sports section
'''
import copy
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess

#To store in DB 
import pandas as pd
import pymongo
from pymongo import MongoClient


def articles_database():
	cluster = MongoClient("mongodb+srv://enihcam:12345@cluster0.irbss.mongodb.net/<News-Collect>?retryWrites=true&w=majority")
	db = cluster["News-Collect"]
	collection = db["The-Guardian"]
	return collection


#Create scrap item for article information
class article_info(scrapy.Item):
	headline = scrapy.Field()
	article_text = scrapy.Field()
	url = scrapy.Field()
	date= scrapy.Field()
	nature = scrapy.Field()


#Class inheritance
class news_spider(scrapy.spiders.Spider):
	name = 'news_spider'
	allowed_domains= ['bbc.com']
	start_urls = ['https://www.bbc.com/']

	#Create database connection
	db = articles_database()

	def clean_html(self,html_text):
		'''
		A function to clean article text
		'''
		soup= BeautifulSoup(html_text,'html.parser')
		soup= soup.get_text()
		return soup


	def parse(self, response):
		'''
		A function to parse the main page to get article links.
		'''
		article_links = response.xpath("//a[@class='block-link__overlay-link']/@href")[1:].extract()
		article_headlines = response.xpath("//a[@class='media__link']/text()").extract()

		for link,headline in zip(article_links,article_headlines):
			article = article_info()
			article['url'] = 'https://www.bbc.com'+link
			article['headline'] = self.clean_html(''.join(headline).strip())

			yield scrapy.Request(article['url'],meta={'Article_info':article},callback=self.parse_article)

	def parse_article(self,response):
		'''
		A function to parse each individual article exists in the main page.
		'''
		article  = response.meta['Article_info']

		text = ''.join(response.xpath("//div[@class='story-body__inner']//p").extract()).strip()
		article['article_text']=self.clean_html(text)

		time = ''.join(response.xpath("//li[@class='mini-info-list__item']/div/text()").extract()).strip()
		article['date']= pd.to_datetime(self.clean_html(time))

		nature = response.xpath("//a[@class='navigation-wide-list__link navigation-arrow--open']/span/text()").extract()
		article['nature'] = nature[0]
		
		#Only stores in database if it's not empty text
		if(text != ''):
			#Set up dictionary to store in the database
			current = {x:article[x] for x in article.keys()}
			current['_id']= current['headline']
			del(current['headline'])
			self.db.insert_one(current)
		yield article 


def retreive():
	process = CrawlerProcess()
	process.crawl(news_spider)
	process.start()

if __name__ == '__main__':
	retreive()