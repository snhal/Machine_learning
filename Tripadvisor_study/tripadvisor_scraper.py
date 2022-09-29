import sys
import os
import json
import codecs
import requests
import time
import csv
import re
from bs4 import BeautifulSoup as BS
import random

class TripAdvisorScraper:

	def __init__(self, city, state):
		self.base_url = "https://www.tripadvisor.com"
		self.user_agents = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36",
		                    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
		                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
		                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
                                    "Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre",
		                    "Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285",
		                    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.1 (KHTML, like Gecko) Maxthon/3.0.8.2 Safari/533.1",
                                    "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16"]
    
		self.current_agent = 0
		self.city = city
		self.state = state
                self.attributes_list = ["Location", "Sleep Quality", "Rooms", "Service", "Value", "Cleanliness"]
    
		hotel_fd = open('traverler_ratings.csv', 'w')
		self.ratings_csv = csv.writer(hotel_fd, delimiter = ',')
    
		attrib_fd = open('attribute_ratings.csv', 'w')
		self.attributes_csv = csv.writer(attrib_fd, delimiter = ',')
    
		outlier_fd = open('outliers.csv', 'w')
		self.outliers_csv = csv.writer(outlier_fd, delimiter = ',')

	def get_html_page(self, url):
		time.sleep(2)
		url = self.base_url + url
		print("Querying URL: " + url)
		headers = { 'User-Agent' : self.user_agents[self.current_agent] }
		self.current_agent = random.randint(0, len(self.user_agents) - 1)
		retries = 0
		while retries < 10:
			try:
				response = requests.get(url, headers = headers)
			except:
				print("--------OOPS Failed--------- Retrying")
				time.sleep(10)
				retries += 1
				if retries < 10:
					continue
				else:
					raise
			break
		return response.text.encode('utf-8')

	def get_tourism_page(self):
		url_city_name = "%20".join(self.city.split())
		url_state_name = "%20".join(self.state.split())
		url = "/TypeAheadJson?query=" + url_city_name + "%20" + url_state_name + "&action=API"
		print("Tourism Page URL: " + url)

		tourism_page = self.get_html_page(url)
		json_obj = json.loads(tourism_page.decode())
		results = json_obj['results']
		urls = results[0]['urls'][0]
		self.tourism_url = urls['url']
		print("Tourism URL: " + self.tourism_url)

	def get_city_hotels(self):
		hotels_page = self.get_html_page(self.tourism_url)
		soup = BS(hotels_page, "lxml")
		hotels_list = soup.find("li", {"class": "hotels twoLines"})
		self.city_hotels_url = str(hotels_list.find('a', href = True)['href'])
		print("City hotels URL: " + self.city_hotels_url)

	def scrape_hotel_details(self):
		query_url = self.city_hotels_url
		while query_url != None:
			hotel_list_page = self.get_html_page(query_url)
			self.extract_fields(hotel_list_page)
			query_url = self.get_next_page(hotel_list_page)

	def get_next_page(self, hotels_page):
		soup = BS(hotels_page, "lxml")
		div = soup.find("div", {"class" : "unified pagination standard_pagination"})
		if div.find('span', {'class' : 'nav next ui_button disabled'}):
			print("Read all pages")
			return None

		hrefs = div.findAll('a', href = True)
		for href in hrefs:
			if href.find(text = True) == 'Next':
				print("Next Page URL: " + href['href'])
				return href['href']
      		return None

	def scrape_reviews_page(self, reviews_page, name):
		soup = BS(reviews_page, 'lxml')
		reviews = soup.findAll('div', {'class': re.compile(r"\s*reviewSelector.*")})
		print("Found " + str(len(reviews)) + " reviews on this page")
		for review in reviews:
			review_id = review['id']
			if review.find('div', {'class': 'col2of2'}) == None:
				continue

			review_url = review.find('div', {'class': 'col2of2'}).find(href = True)['href']
			review_page = self.get_html_page(review_url)
			self.scrape_single_review(review_page, name, review_id, review_url)

	def scrape_single_review(self, review_page, name, review_id, review_url):
		soup = BS(review_page, 'lxml')
		ratings = soup.find('ul', {'class': 'recommend'})
		if ratings == None:
			self.outliers_csv.writerow([review_url, str(review_id)])
			return

		summary_list = ratings.findAll('li', {'class': 'recommend-answer'})
		if len(summary_list) == 0:
			self.outliers_csv.writerow([review_url, str(review_id)])
			return

		for item in summary_list:
			for attribute in self.attributes_list:
				if item.find('div', {'class': 'recommend-description'}).find(text = True) == attribute:
					stars = item.find('img', {'class': re.compile(r'sprite-rating_ss_fill rating_ss_fill.*')})['alt'].split(" ")[0]
					self.attributes_csv.writerow([str(name), str(review_id), str(attribute), str(stars)]) 
					print("Name: " + str(name) + " Attrib: " + attribute + " Stars: " + str(stars))

	def get_next_reviews_page(self, reviews_page):
		soup = BS(reviews_page, 'lxml')
		div = soup.find('div', {'class': 'unified pagination '})
		if div.find('span', {'class' : 'nav next disabled'}):
			print("Read all reviews")
			return None

		hrefs = div.findAll('a', href = True)
		for href in hrefs:
			if href.find(text = True) == 'Next':
				print("Next Page URL: " + href['href'])
				return href['href']
                return None

	def scrape_reviews_of_hotel(self, reviews_url, name):
		while reviews_url != None:
			reviews_page = self.get_html_page(reviews_url)
			self.scrape_reviews_page(reviews_page, name)
			reviews_url = self.get_next_reviews_page(reviews_page)

	def extract_fields(self, hotels_page):
		soup = BS(hotels_page, 'lxml')
		hotel_boxes = soup.findAll('div', {'class' :'listing easyClear p13n_imperfect '})
    
		for hotel_box in hotel_boxes:
			name = hotel_box.find('div', {'class' :'listing_title'}).find(text = True)
			try:
				rating = hotel_box.find('div', {'class' : 'listing_rating'})
				reviews = rating.find('span', {'class' : 'more'}).find(text = True).split(' ')[0]
				stars = hotel_box.find('img', {'class' : 'sprite-ratings'})['alt'].split(' ')[0]
			except Exception:
				print("No ratings for this hotel")
				reviews = "N/A"
				stars = 'N/A'

			self.ratings_csv.writerow([str(name), str(stars), str(reviews)])
			print("Name: " + str(name) + " Reviews: " + str(reviews) + " Stars: " + str(stars))

			reviews_url = hotel_box.find('div', {'class' :'listing_title'}).find(href = True)['href']
			self.scrape_reviews_of_hotel(reviews_url, name)

      
if __name__ == "__main__":
	scraper = TripAdvisorScraper('boston', 'massachusetts')
	scraper.get_tourism_page()
	scraper.get_city_hotels()
	scraper.scrape_hotel_details()
