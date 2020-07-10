import shutil
import pymongo
from pymongo import MongoClient
import pandas as pd
import pprint
import re


#Get size of terminal for printing 
columns = shutil.get_terminal_size().columns

#Read The DataBase
class stopItr(Exception):pass

class pipeline():
	def __init__(self,meta=None):
		self.cluster = MongoClient("mongodb+srv://enihcam:12345@cluster0.irbss.mongodb.net/<News-Collect>?retryWrites=true&w=majority")
		self.db = self.cluster["News-Collect"]
		self.collection = self.db["The-Guardian"]

		if isinstance(meta,dict):
			if(len(meta.keys()) == 2):
				self.find(meta)
			else:
				if('title' in meta.keys()):
					self.get_bytitle(meta)
				else:
					self.get_bydate(meta)

		else:
			self.navigate()

	def __print(self,article):
		#to save lines of code
		print(str(article['_id']).center(columns))
		print('Article Section: '+str(article['nature']))
		print('Article Date: '+str(article['date']))
		print('\n')
		print(article['article_text'])
		print('\n')


	def get_bydate(self,meta):
		articles = self.collection.find({'date':{"lt":meta['date']}}).limit(5)
		for article in articles:
			self.__print(article)

	def find(self,meta):
		i=0
		expression = re.compile(meta['keyword'],re.IGNORECASE)
		for article in self.collection.find({'article_text':expression}):
			if(i %meta['limit'] == (meta['limit']-1)):
				char = input('press any key to continue searching or q to quit :')
				if(char =='q'):
					break
			else:			
				self.__print(article)

	def get_bytitle(self,meta):
		expression = re.compile(meta['title'],re.IGNORECASE)
		article = self.collection.find_one({'_id':expression})
		self.__print(article)
		return

	def navigate(self):
		print('press any key to continue navigation or q to quit: ...')
		i = 0
		while(True):
			try:
				for article in self.collection.find({}):
					char = input()
					if(char!='q'):
						self.__print(article)
						i+=1
					elif (char =='q'):
						raise stopItr
			except (stopItr):
				break

def interface():
	meta = {}
	print("__Read Articles API__\n".center(columns))
	print("Navigate through articles : press 1 ")
	print("Find article by a keyword : press 2 ")
	print("Find article by title : press 3")
	print("Find article by date : press 4")

	choice = input()
	if (choice=='1'):
		meta=1
	elif (choice=='2'):
		meta['keyword'] = input("Please write the keyword/genrexpression you are looking for in any article text: ")
		meta['limit'] = int(input("Please specity the maximum number of articles to find : "))

	elif (choice =='3'):
		meta['title']= input("Please write a definitive title: ")

	elif (choice =='4'):
		date  = input("Please enter the date in the following format (dd mm year): ")
		meta['date'] = pd.to_datetime(date)
	else:
		meta = None
		assert 'please specify a number between 1 and 2'

	print('\n')
	return meta

if __name__ == '__main__':

	meta_data = interface()
	db_pipeline = pipeline(meta_data)

	