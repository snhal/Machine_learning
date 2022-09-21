import pandas as pd
import json
import operator
import collections
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as met
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist
import sklearn.mixture

class YelpStudy():       
    def __init__(self):
        self.data = []
        self.top_categories = []
        
##############################################################################################################
# read_data: reads all records in "yelp_academic_dataset_business.json" and creates a dictionary of the 
# most popular categories. 
##############################################################################################################
        
	def read_data():
		category_counts = {}
		f = open("yelp_academic_dataset_business.json","r")
	
		for line in f:
			js = json.loads(line)
			self.data.append(js)
		
		print("total records read : " + str(len(self.data)))
		
		for i in range(0,len(self.data)):
			d = self.data[i]
			if "categories" in self.data[i]:
				lst = d["categories"]
				if "Restaurants" in lst:
					for j in range(0,len(lst)):
						if(lst[j]!="Restaurants"):
							category = lst[j]
							if category in category_counts:
								category_counts[category] = category_counts[category] + 1
							else:
								category_counts[category] = 0
			else:
				print("category not found for :" + str(self.data[i]))

		for k,v in category_counts.items():
			print(k + "-----> " + str(v))

		category_counts_sorted = sorted(category_counts.items(),key=operator.itemgetter(1),reverse=True)
		category_counts_ordered = collections.OrderedDict(category_counts_sorted)

		count = 0
		for k,v in category_counts_ordered.items():
			if(count<20):
				self.top_categories.append(k)
				count = count + 1	
                

##############################################################################################################
# select_data: selects records with restaurants in 'Las Vegas' and appends them to a list input_lst[]. 
# Then converts this list to a dataframe. Calls labelEncoder() and OneHotEncoder() methods from sklear.pre-
# processing to format categorical input fields - "categories". Output from OneHotEncoder() is scaled and
# KMeans is applied to identify clusters.
# input_lst contains "business_id", "latitude", "longitude",and all categories - cat1, cat2...etc. If a record 
# has 'a' categories 'a' items are appended to input_lst.
#############################################################################################################

	def select_data():
		input_lst = []*20

		for i in range(0,len(self.data)):
			d = self.data[i]

			if (("city" in d) and (d["city"] == "Las Vegas")):
				temp = []
				temp.append(d["business_id"])
				temp.append(d["latitude"])
				temp.append(d["longitude"])
	
				if("Restaurants" in d["categories"]):
					for j in range(0,len(d["categories"])):

						if((d["categories"][j]!="Restaurants") and 
						(d["categories"][j] in self.top_categories)):

							temp.append(d["categories"][j])

					input_lst.append(temp)
		df = pd.DataFrame(input_lst)
		df.fillna(value="$$",inplace=True)

		le = preprocessing.LabelEncoder()
		for i in range(3,len(df.columns)):
			df[i] = le.fit_transform(df[i])

		enc = OneHotEncoder()
		obj = enc.fit_transform(df[df.columns[3:]])
		arr = obj.toarray()
		df2 = pd.DataFrame(arr)

		df3 = pd.concat([df[df.columns[1:3]],df2],axis=1)
		arr_scaled = preprocessing.scale(df3)
        return arr_scaled


###############################################################################################################
# kmeans_clusters: On running this method with multiple "no of clusters", it is found that 3 clusters maximize 
# the silhouette coefficient.
###############################################################################################################

	def kmeans_clusters(arr_scaled):
		print("Kmeans computation begins....")
		num = 3

		for i in range(0,6):
			kmeans = KMeans(init='k-means++',n_clusters=num,n_init=10)
			kmeans.fit_predict(arr_scaled)
			error = kmeans.inertia_
			print(" Total error with " + str(num) + " clusters = " + str(error))
			num = num + 1

			score = met.silhouette_score(arr_scaled,kmeans.labels_,metric='euclidean',
			sample_size=1000)
			
			print("silhoutte coefficent : " + str(score))

		kmeans = KMeans(init='k-means++',n_clusters=3,n_init=100)
		kmeans.fit_predict(arr_scaled)

		pca_2 = PCA(2)
		plot_columns = pca_2.fit_transform(arr_scaled)
		
		plt.xlabel("Latitude")
		plt.ylabel("Longitude")
		plt.title("K-means++ clustering")
        
		i=0		
		for sample in plot_columns:
			if kmeans.labels_[i] == 0:
				plt.scatter(sample[0],sample[1],color="c",s=75,marker="o")
			if kmeans.labels_[i] == 1:
				plt.scatter(sample[0],sample[1],s=75,marker="*",color="chartreuse")
			if kmeans.labels_[i] == 2:
				plt.scatter(sample[0],sample[1],color="green",s=75,marker="v")
			if kmeans.labels_[i] == 3:
				plt.scatter(sample[0],sample[1],color="cyan",s=75,marker="^")
			i += 1
		plt.show()

        
############################################################################################################
# instantiate YelpStudy. Read and process data.
############################################################################################################

yelp_obj = YelpStudy()
yelp_obj.read_data()       
arr_scaled = yelp_obj.select_data()
yelp_obj.kmeans_clusters(arr_scaled)



