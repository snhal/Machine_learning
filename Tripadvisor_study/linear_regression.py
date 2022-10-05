import pandas as pd
import sys
import csv
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf

class LinearRegression:
	def __init__(self):
		self.input = []
		self.formatted_attribute_scores = []
		self.formatted_hotel_ratings = []
		self.init_attribute_rating_vars()
		self.init_traveller_rating_vars()
		print("Initialization complete")

	def init_attribute_rating_vars(self):
		self.sum_service = 0
		self.sum_clean = 0
		self.sum_value = 0
		self.sum_sleep = 0
		self.sum_rooms = 0
		self.sum_location = 0
		self.count_service = 0
		self.count_clean = 0
		self.count_value = 0
		self.count_sleep = 0
		self.count_rooms = 0
		self.count_location = 0
        
	def init_traveller_rating_vars(self):
		self.sum_ratings = 0
		self.count_ratings = 0

############################################################################################################################
# Read attribute_ratings file. For every hotel find each attribute's average and save it in this format: hotel_name, 
# attribute1_score, attribute2_score...attribute6_score for all 6 attributes- service, cleanliness, value, sleep_quality, 
# room and location
############################################################################################################################

	def read_attribute_rating(self):
		f = open("attribute_rating.txt","r")
		for line in f:
			line_list = line.split(":")
			if line_list[1] == "Business service (e.g., internet access)":
				continue
			if line_list[1] == "Check in / front desk":
				continue
			else:
				temp = []
				temp.append(line_list[0])
				temp.append(line_list[1])
				temp.append(int(line_list[2]))
				temp.append(int(line_list[3]))
				self.input.append(temp)   
        
		self.init_attribute_rating_vars()
		reference_hotel = self.input[0][0]
		for i in range(0,len(self.input)):
			row = self.input[i]
			if(reference_hotel == row[0]):
				self.find_cumulative_attribute_ratings(row)
			else:
				hotel_scores = self.compute_attribute_scores(reference_hotel)                
				self.formatted_attribute_scores.append(hotel_scores)
				reference_hotel = self.input[i][0]
				self.init_attribute_rating_vars()
				self.find_cumulative_attribute_ratings(row)
                hotel_scores = self.compute_attribute_scores(reference_hotel)                
                self.formatted_attribute_scores.append(hotel_scores)

	def find_cumulative_attribute_ratings(self, row):
		if(row[1] == 'Service'):
			self.sum_service = self.sum_service + row[2]*row[3]
			self.count_service = self.count_service + row[3]
		elif(row[1] == 'Cleanliness'):
			self.sum_clean = self.sum_clean + row[2]*row[3]
			self.count_clean = self.count_clean + row[3]
		elif(row[1] == 'Value'):
			self.sum_value = self.sum_value + row[2]*row[3]
			self.count_value = self.count_value + row[3]
		elif(row[1] == 'Sleep Quality'):
			self.sum_sleep = self.sum_sleep + row[2]*row[3]
			self.count_sleep = self.count_sleep + row[3]
		elif(row[1] == 'Rooms'):
			self.sum_rooms = self.sum_rooms + row[2]*row[3]
			self.count_rooms = self.count_rooms + row[3]
		elif(row[1] == 'Location'):
			self.sum_location = self.sum_location + row[2]*row[3]
			self.count_location = self.count_location + row[3]
                    
	def compute_attribute_scores(self, reference_hotel):
		hotel_scores = []
		hotel_scores.append(reference_hotel)
		if(self.count_service == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_service / self.count_service))

		if(self.count_clean == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_clean / self.count_clean))

		if(self.count_value == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_value / self.count_value))

		if(self.count_sleep == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_sleep / self.count_sleep))

		if(self.ccount_rooms == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_rooms / self.count_rooms))

		if(self.count_location == 0):
			hotel_scores.append(0)
		else:
			hotel_scores.append(np.float(self.sum_location / self.count_location))
		return hotel_scores
    
#############################################################################################################################
# Read traveller_ratings file. Compute ratings average for each hotel and save it in this format: hotel_name, average_rating
#############################################################################################################################

	def read_traveller_rating(self):
		op = open("traveller_ratings.csv", "r")	
		f = csv.reader(op)
		traveller_ratings = []
		for line in f:
			if(line[1] == "Excellent"):
				value = 5
			elif(line[1] == "Very good"):
				value = 4
			elif(line[1] == "Average"):
				value = 3
			elif(line[1] == "Poor"):
				value = 2
			elif(line[1] == "Terrible"):
				value = 1  
			temp = []
			temp.append(line[0])
			temp.append(value)
			total_ratings = line[2].replace("," ,"")
			temp.append(int(total_ratings))
			traveller_ratings.append(temp)

		reference_hotel = traveller_ratings[0][0]
		self.init_traveller_rating_vars()
		for i in range(0,len(traveller_ratings)):
			if(reference_hotel == traveller_ratings[i][0]):
				self.find_cumulative_traveller_ratings(traveller_ratings[i])                
			else:
				self.compute_traveller_ratings_scores(reference_hotel)                
				reference_hotel = traveller_ratings[i][0]
				self.init_traveller_rating_vars()
				self.find_cumulative_traveller_ratings(traveller_ratings[i]) 
		self.compute_traveller_ratings_scores(reference_hotel)                

	def find_cumulative_traveller_ratings(self,ratings):
		self.sum_ratings = self.sum_ratings + (ratings[1] * ratings[2])
		self.count_ratings = self.count_ratings + ratings[2]
    
	def compute_traveller_ratings_scores(self, reference_hotel):
		temp = []
		temp.append(reference_hotel)
		if self.count_ratings == 0:
			weighted_avg = 0
		else:
			weighted_avg = self.sum_ratings / self.count_ratings
		temp.append(weighted_avg)
		self.formatted_hotel_ratings.append(temp)

###########################################################################################################################
# Fit a linear regression model, remove column1-hotel_name from the dataframe. Rows with index 50 and 51 have high leverage
# and high residual values on the influence plot. So exclude these rows before creating a linear regression model. R-square 
# improves considerably on excluding these two records.
###########################################################################################################################

	def process_input(self):
		predictors = pd.DataFrame(sorted(self.formatted_attribute_scores,key = lambda k: k[0]),
		columns = ['Hotel', 'Service', 'Cleanliness', 'Value', 'Sleep_Quality', 'Rooms', 'Location'])

		response = pd.DataFrame(sorted(self.formatted_hotel_ratings,key = lambda k: k[0]),
		columns = ['Hotel_name', 'Rating']) 

		response_subset = response[response.columns[1]]
		predictors_subset = predictors[predictors.columns[1:]]
		df = pd.concat([response_subset, predictors_subset], axis=1)
		sub = ~df.index.isin([50, 51])
		model = smf.ols(data=df, formula="Rating ~ Service + Cleanliness + Value + Sleep_Quality + Rooms + Location -1", subset = sub)
		res = model.fit()
		print(res.summary())
		fig = sm.graphics.influence_plot(res, criterion="cooks")
		plt.show()

        
if __name__ == "__main__":
    linear_regression = LinearRegression()
    linear_regression.read_attribute_rating()
    linear_regression.read_traveller_rating()
    linear_regression.process_input()
