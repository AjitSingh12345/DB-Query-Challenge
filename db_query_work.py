# -*- coding: utf-8 -*-
"""DB Query Work

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nDQsrHgQkfBVeovSeg4HIuGAH04C59AJ
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
from sklearn.model_selection import train_test_split
from mlxtend.plotting import plot_confusion_matrix
import matplotlib.cm as cm
from matplotlib import rcParams
from collections import Counter
from nltk.tokenize import RegexpTokenizer
import re
import string
import csv
from tensorflow.keras.layers import LSTM, Activation, Dense, Dropout, Input, Embedding
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing import sequence
# %matplotlib inline

import warnings
warnings.filterwarnings("ignore")

from google.colab import drive
drive.mount('/content/drive')

df_people = pd.read_excel('/content/Advancement Tech Internship - Sample Data - Tech Exercise Anonymized.xlsx', 
                          dtype={'PID': str, 'FirstName': str, 'LastName': str, 'Age': int, 'MaritalStatus': str, "County": str, "PrimaryAddressState": str,
                                 "PrimaryAddressCountry": str, "RatingCode": str, "Rating": str, "Giving": str})  

#df_people = df_people.reindex(["$0", "< $2,500", "$2,500 - $9,999", "$10,000 - $24,999", "$25,000 - $49,999", "$50,000 - $99,999", "$100,000 - $249,999", 
#           "$250,000 - $499,999", "$500,000 - $999,999", "$1M - $4.99M"])

print(df_people.columns)
print(df_people.info())
print(df_people.describe(include='all'))

grouped_df_people = df_people.groupby(['Giving']).mean()
 print(grouped_df_people['Age'])
 
df_gavemax_people = (df_people[df_people['Rating'] == df_people['Giving']])
print (df_gavemax_people[df_gavemax_people['PrimaryAddressState'] == 'Illinois'])
print(df_gavemax_people.describe(include='all'))

print(df_people.plot.scatter(x='Age',
                      y='Giving',
                      c='Blue'))

print(df_people.plot.scatter(x='RatingCode',
                      y='Giving',
                      c='Red'))

print(df_people.plot.scatter(x='PrimaryAddressState',
                      y='Giving',
                      c='Green'))


print(df_people.plot.scatter(x='MaritalStatus',
                      y='Giving',
                      c='Blue'))


donation_sizes = df_people['Giving'].value_counts()
print(donation_sizes)

#print(df_people.plot.hist(x='Giving'))

print(df_people.describe(include=[object]))

print()
print(df_people['PrimaryAddressState'].describe(include=[object]))

print()
print(df_people['County'].describe(include=[object]))

print()
print(df_people['PrimaryAddressCountry'].describe(include=[object]))

print()
print(df_people['MaritalStatus'].describe(include=[object]))

grouped_df_people = df_people.groupby(['MaritalStatus']).mean()
 print(grouped_df_people['Age'])

print()
print()
plt.figure(figsize=(20,10))
sns.countplot(x='Giving', data=df_people)
plt.show()

print()
print()
plt.figure(figsize=(20,10))
sns.countplot(x='Giving', hue='MaritalStatus', data=df_people)
plt.show()

print()
print()
plt.figure(figsize=(30,15))
plt.ylim(0,100)
sns.countplot(x='Giving', hue='PrimaryAddressState', data=df_people)
plt.show()

plt.figure(figsize=(20,10))
sns.boxplot(x='Age', y='Giving', data=df_people)
plt.show()

def feature_interactions(df,feature1, feature2,continuous_col, color_):
  group = df.groupby([feature1,feature2],as_index=False)[continuous_col].mean().reset_index(drop=True)
  pivot = group.pivot(index=feature1, columns=feature2, values=continuous_col)
  pivot.fillna(0, inplace=True)
  plt.figure(figsize=(20,12))
  sns.heatmap(pivot,cmap=color_)
  plt.show()

feature_interactions(df_people,'Giving','MaritalStatus','Age', 'Blues')

feature_interactions(df_people,'Giving','County','Age', 'Greens')

feature_interactions(df_people,'Giving','PrimaryAddressState','Age', 'Oranges')

feature_interactions(df_gavemax_people,'Giving','MaritalStatus','Age', 'Blues')

feature_interactions(df_gavemax_people,'Giving','County','Age', 'Greens')

feature_interactions(df_gavemax_people,'Giving','PrimaryAddressState','Age', 'Oranges')

# Findings:

# Most people have a max potential $10k-$25k, most people give <$2500
# Abt ½ people gave <$2.5k
# Positive correlation between age and giving amount… $1M-5M is outlier as avg age decreases from 88 to 69. (could be cuz of small sample size for $1M-5M)
# 66 people gave as much as they could (44 from Illinois = ⅔) … which on avg was <$2.5k for ⅔ (43) of them.   
# Age ranges get smaller (with higher age values) as giving amount increases
# giving amount inversely proportional to # of states ppl donate from 
# Partnered, separated, divorced are nonoptimal groups  to pursue
# Married > widow > single … are optimal groups to pursue
# Most of the data (>.5) comes from people who are married

# Questions:

# Track people who move into new ratingCode groups, we can estimate what percentage of their rating (max potential) they give, then this may stay constant as they move to larger rating groups … (premium donors)
# For what duration of time have they been donating?

df_relat = pd.read_excel('/content/relationships.xlsx', dtype={'RelationshipSet': str, 'PLID': str, 'P1RelationshiopTypeID': str, 'P1RelationshipType': str, 
                                                               'P2ID': str, 'P2RelationshipTypeID': str, "P2RelationshipType": str})  
# df_relat

# print(df_relat.columns)
# print(df_relat.info())
# print(df_relat.describe(include='all'))

df_siblings = (df_relat[df_relat['P2RelationshipType'] == 'Sibling'])
print(df_siblings)
print()

df_cousins = (df_relat[df_relat['P2RelationshipType'] == 'Cousin'])
print(df_cousins)
print()

df_partner = (df_relat[df_relat['P2RelationshipType'] == 'Spouse/Partner'])
print(df_partner)
print()

df_aunt_nephew = (df_relat[df_relat['P2RelationshipType'] == 'Niece/Nephew']) 
print(df_aunt_nephew)
print()

df_relative = (df_relat[df_relat['P2RelationshipType'] == 'Relative']) 
print(df_relative)
print()

df_parents = (df_relat[df_relat['P2RelationshipType'] == 'Parent']) 
print(df_parents)
print()

df_inlaws = (df_relat[df_relat['P2RelationshipType'] == 'In-law']) 
print(df_inlaws)
print()

df_grandparents = (df_relat[df_relat['P2RelationshipType'] == 'Grandchild']) 
print(df_grandparents)
print()

# print (df_gavemax_people[df_gavemax_people['PrimaryAddressState'] == 'Illinois'])

# -make plots comparing avg giving amount for each relationship type
# -find counts of each relationship type

# - make for loop to go through each row in df_people and for each row, go throgh an entire column of IDs per relationship type, 
# if the id matches any in the relationship type, then add entire row from df_people to new dataframe

# for (each row in df_people) {
#     for (each row in col of sibling IDs) {
#         if (PID in row == sibling ID) {
#             add row from df_people into df_sibling_people... 
#         }
#     }
# }

# ... repeat for all 8 relationship types
# - then do a giving amount X count histogram for each 8 relationship dataframes

def find_reltype_ids(data, output_arr):
  for index, row in data.iterrows():
      output_arr.append(row['PLID'])

sibling_ids = []
find_reltype_ids(df_siblings, sibling_ids)
print(sibling_ids)

child_ids = []
find_reltype_ids(df_parents, child_ids)
print(child_ids)

aunt_ids = []
find_reltype_ids(df_aunt_nephew, aunt_ids)
print(aunt_ids)

cousin_ids = []
find_reltype_ids(df_cousins, cousin_ids)
print(cousin_ids)

grandchild_ids = []
find_reltype_ids(df_grandparents, grandchild_ids)
print(grandchild_ids)

inlaw_ids = []
find_reltype_ids(df_inlaws, inlaw_ids)
print(inlaw_ids)

relative_ids = []
find_reltype_ids(df_relative, relative_ids)
print(relative_ids)

partner_ids = []
find_reltype_ids(df_partner, partner_ids)
print(partner_ids)

def who_gave_what(data, arr_who, out_arr):
  for index, row in data.iterrows():
    for x in arr_who:
      if row['PID'] == x:
        out_arr.append(row['Giving'])

partners_gave = []
who_gave_what(df_people, partner_ids, partners_gave)
print(partners_gave)
df_partnergave = pd.DataFrame(partners_gave, columns=['Amount Gave'])

aunts_gave = []
who_gave_what(df_people, aunt_ids, aunts_gave)
print(aunts_gave)
df_auntuncgave = pd.DataFrame(aunts_gave, columns=['Amount Gave'])

childs_gave = []
who_gave_what(df_people, child_ids, childs_gave)
print(childs_gave)
df_childgave = pd.DataFrame(childs_gave, columns=['Amount Gave'])

cousins_gave = []
who_gave_what(df_people, cousin_ids, cousins_gave)
print(cousins_gave)
df_cousgave = pd.DataFrame(cousins_gave, columns=['Amount Gave'])

grandparents_gave = []
who_gave_what(df_people, grandchild_ids, grandparents_gave)
print(grandparents_gave)
df_grandgave = pd.DataFrame(grandparents_gave, columns=['Amount Gave'])

inlaws_gave = []
who_gave_what(df_people, inlaw_ids, inlaws_gave)
print(inlaws_gave)
df_inlawgave = pd.DataFrame(inlaws_gave, columns=['Amount Gave'])

relatives_gave = []
who_gave_what(df_people, relative_ids, relatives_gave)
print(relatives_gave)
df_relgave = pd.DataFrame(relatives_gave, columns=['Amount Gave'])

siblings_gave = []
who_gave_what(df_people, sibling_ids, siblings_gave)
print(siblings_gave)
df_sibgave = pd.DataFrame(siblings_gave, columns=['Amount Gave'])

print("Aunt & uncle: ", df_auntuncgave.value_counts())
print()
print("child and parents: ", df_childgave.value_counts())
print()
print("cousins: ", df_cousgave.value_counts())
print()
print("grandparents & grandchildren: ", df_grandgave.value_counts())
print()
print("in laws: ", df_inlawgave.value_counts())
print()
print("relatives: ", df_relgave.value_counts())
print()
print("siblings: ", df_sibgave.value_counts())
print()
print("partners: ", df_partnergave.value_counts())
print()

plt.figure(figsize=(16,8))
sns.countplot(x='Amount Gave', data=df_grandgave)
plt.show()

plt.figure(figsize=(16,8))
sns.countplot(x='Amount Gave', data=df_inlawgave)
plt.show()

plt.figure(figsize=(16,8))
sns.countplot(x='Amount Gave', data=df_cousgave)
plt.show()

plt.figure(figsize=(16,8))
sns.countplot(x='Amount Gave', data=df_sibgave)
plt.show()

# Findings:

# Most of relationships were spouse/partner then siblings, though they were fairly evenly distributed
# Very few grandchild/grandparent relationships
# **cousins gave 7 $1-5M donations?
# Grandparents, relatives are nonoptimal 
# Inlaws gave 4 $1-5m donations
# Siblings, & aunt/uncle gave large amount in 6-fig range