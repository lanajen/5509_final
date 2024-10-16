# -*- coding: utf-8 -*-
"""5509_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aG2TuBdQZBQe_BJXY3suT_OXC621TSYP

#Crime Data of San Francisco

DTSA 5509 Final - Introduction to Machine Learning: Supervised Learning

Steps:

1. Description of the supervised learning problem
2. Exploratory Data Analysis
3. Model analysis: building and training the model
4. Results
5. Discussion and conclusion

###Step 1: Description of the supervised learning problem

Because crime is an ongoing and significant issue in cities, my project aims to provide insight on the realities of crime statistics. News and crime reporting in the media may impress a false narrative, so my goal is to balance out the fear with data.  

The supervised learning aspect focuses on using patterns in the dataset to build a model that anyone can use to stay more informed. The most successful model in my project is one that sheds light on crime at different altitudes/elevations.

###Step 2: Exploratory Data Analysis
In this step, the goals include: acquiring and storing the data, exploring initial questions, seeing if data could provide insight.

The actions include deleting data appropriately, adding more data, and transforming data to create a more useful dataset.

#### Data Acquisition

SFPD provides a free dataset of crime reports dating back to 2018 from https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783/data_preview

Downloaded data as csv file, stored locally.
"""

# Commented out IPython magic to ensure Python compatibility.
# Import all necessary libraries
import scipy as sp
import scipy.stats as stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import math
from dateutil import parser
import requests
import time

sns.set()
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
# %matplotlib inline

"""#### Load and inspect data

This path works when using an uploaded file in Colab. Path may need to be modified for different environments.
"""

df = pd.read_csv('/content/Police_Department_Incident_Reports__2018_to_Present_20241013.csv')

# First glimpse at dataset
df.info()

# Drop all columns that are some mostly empty or are irrelevant
# Dropping columns was an iterative process - columns were decided on
# after cycles of looking at and trying to use the column's data

df = df.drop(columns=[
    'CAD Number',
    'Report Type Code',
    'Report Type Description',
    'Filed Online',
    'Intersection',
    'Supervisor District',
    'Supervisor District 2012',
    'ESNCAG - Boundary File',
    'Central Market/Tenderloin Boundary Polygon - Updated',
    'Civic Center Harm Reduction Project Boundary',
    'HSOC Zones as of 2018-06-05',
    'Invest In Neighborhoods (IIN) Areas',
    'Current Supervisor Districts' ,
    'Current Police Districts',
    'Row ID',
    'Incident ID',
    'Incident Number',
    'Neighborhoods',
    'Resolution',
    'Police District',
    'Analysis Neighborhood',
    'CNN',
    'Police District',
    'Incident Code',
    'Incident Description',
    'Point'])

df.describe()

# Exploration question: how many unique and null values per column?
for f in df.columns:
  uni = df[f].unique().size
  count = 0
  for i in df[f]:
    if isinstance(i, float):
      if math.isnan(i):
        count += 1
  print(f, ":", uni, "unique,", count, "NaN's")

# Functions for converting time differences to a more usable form
def time_diff(incident_time, report_time):
    t1 = parser.parse(incident_time)
    t2 = parser.parse(report_time)
    return abs((t2 - t1))

def min_diff(incident_time, report_time):
    t1 = parser.parse(incident_time)
    t2 = parser.parse(report_time)
    return ((t2 - t1).total_seconds()/60.0)

# Adding more data: time difference between incident and reporting
diff = []
minutes = []
midnight = "00:00"
time_from_midnight = []
for j in range(df['Incident Datetime'].size):
  min = min_diff(df['Incident Datetime'][j],df['Report Datetime'][j])
  from_midnight = (math.floor(min_diff(midnight,df['Incident Time'][j])/60.0))
  time_from_midnight.append(from_midnight)
  minutes.append(min)

df.insert(6, "Minutes Til Report", minutes) #minutes between incident and reporting
df.insert(7, "Incident Time Hour", time_from_midnight) #time of incident, by the hour

# Add more data: Conversion of day of week to numerical
week_number = []
for l in df['Incident Day of Week']:
  day = 0
  if l == "Monday":
    day = 1
  elif l == "Tuesday":
    day = 2
  elif l == "Wednesday":
    day = 3
  elif l == "Thursday":
    day = 4
  elif l == "Friday":
    day = 5
  elif l == "Saturday":
    day = 6
  else:
    day = 7
  week_number.append(day)

df.insert(5, "Day Number", week_number)

#look at new data
df.head()

#Exploration question: does crime occur more in certain parts of the day? Plus plot
stage = df.groupby('Incident Time Hour')['Incident Datetime'].count()
times = []
for c in stage:
  times.append(c)
arr = sorted(df['Incident Time Hour'].unique())
data = {'Time': arr,
        'Incidents': times}

df_time_incident = pd.DataFrame(data)

plt.plot(df_time_incident.Time, df_time_incident.Incidents)
plt.title("Incident levels through the day, raw")
plt.xlabel("Hour of day, 24 hours")
plt.ylabel("Number of incidents")

#Exploration question: does crime occur more in certain days of the week? Plus plot
stage = df.groupby('Day Number')['Incident Datetime'].count()
times = []
for g in stage:
  times.append(g/1000.0)
arr1 = sorted(df['Day Number'].unique())
data1 = {'Day': arr1,
        'Incidents': times}

df_day_incident = pd.DataFrame(data1)

plt.plot(df_day_incident.Day, df_day_incident.Incidents)
plt.title("Crime As Week Progresses")
plt.xlabel("Starts with Monday")
plt.ylabel("Incidents in the 1000s")

# How many crimes in each category?
df.groupby('Incident Category')['Incident Datetime'].count()

# Any correlations between columns?
df.corr(numeric_only=True)

# Exploration question: any correlations amongst traffic collision incidents?
traffic = df[df['Incident Category']=="Traffic Collision"]
traffic.corr(numeric_only=True)

# Exploration question: any correlations in warrant-related incidents?
warr = df[df['Incident Category']=="Warrant"]
warr.corr(numeric_only=True)

# Exploration question: any correlations within disorderly conduct?
disorder = df[df['Incident Category']=="Disorderly Conduct"]
disorder.corr(numeric_only=True)

# Exploration question: any correlations in drug-related incidents?
drug = df[df['Incident Category']=="Drug Offense"]
drug.corr(numeric_only=True)

# Clean data further for elevation investigation
#remove NaN from whole df and reset index
df = df[df['Latitude'].notna()]
df = df[df['Longitude'].notna()]
df = df.reset_index()

# Add data: new empty column for land elevation based on coordinates
df["Elevation"] = np.nan

# Function for getting elevation from external source
def get_elevation(lat, long):
    # query = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{long}" #this source gives bad data!!
    # re = requests.get(query).json()
    time.sleep(0.5)
    query = ('https://api.open-elevation.com/api/v1/lookup'f'?locations={lat},{long}')
    r = requests.get(query).json()
    e = pd.json_normalize(r, 'results')['elevation'].values[0]
    return e

# Request elevation data and populate Elevation column
elevations = [] #save externally since API is buggy
for m in range(df['Latitude'].size):
    lat = df['Latitude'][m]
    e = get_elevation(lat, df['Longitude'][m])
    df.loc[m, "Elevation"] = e
    elevations.append(e)
print(elevations)

print(len(elevations))

# check out the goods
df.describe()

# Data organizing: new table containing rows that have elevation
df2 = df[df['Elevation'].notna()]

df2=df2.reset_index()

"""Exploration: There seems to be a correlation between elevation and crime"""

# Grouping elevation to 10 meter chunks
neg = 0
p10= 0
p20= 0
p30= 0
p40= 0
p50= 0
p60= 0
p70= 0
p80= 0
p90= 0
p100= 0
p110= 0
p120= 0
p130= 0
p140= 0
p150= 0
p160= 0
p170= 0
p180= 0
p190= 0
p200= 0
p210= 0
p220= 0
p230= 0
p240= 0
p250= 0
p260= 0
p270= 0

for e in df2["Elevation"]:
  if e < 0:
    neg += 1
  elif e < 10:
    p10 += 1
  elif e < 20:
    p20 += 1
  elif e < 30:
    p30 += 1
  elif e < 40:
    p40 += 1
  elif e < 50:
    p50 += 1
  elif e < 60:
    p60 += 1
  elif e < 70:
    p70 += 1
  elif e < 80:
    p80 += 1
  elif e < 90:
    p90 += 1
  elif e < 100:
    p100 += 1
  elif e < 110:
    p110 += 1
  elif e < 120:
    p120 += 1
  elif e < 130:
    p130 += 1
  elif e < 140:
    p140 += 1
  elif e < 150:
    p150 += 1
  elif e < 160:
    p160 += 1
  elif e < 170:
    p170 += 1
  elif e < 180:
    p180 += 1
  elif e < 190:
    p190 += 1
  elif e < 200:
    p200 += 1
  elif e < 210:
    p210 += 1
  elif e < 220:
    p220 += 1
  elif e < 230:
    p230 += 1
  elif e < 240:
    p240 += 1
  elif e < 250:
    p250 += 1
  elif e < 260:
    p260 += 1
  else:
    p270 += 1

d = {'Elevation': [0, 10, 20, 30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270],
      'Incidents': [neg, p10,p20,p30,p40,p50,p60,p70,p80,p90,p100,p110,p120,p130,p140,p150,p160,p170,p180,p190,p200,p210,p220,p230,p240,p250,p260,p270]}

# Create df for grouped elevation
df_elevation = pd.DataFrame(d)

# How many crimes in each elevation level?
# even with a small dataset, there is a pattern than crime decreses with elevation
plt.plot(df_elevation.Elevation, df_elevation.Incidents)

fraud_clean = df2[df2['Incident Category']=="Fraud"] #somewhat small
print(fraud_clean.shape)
fraud_clean.corr(numeric_only=True)

assult_clean = df2[df2['Incident Category']=="Assault"] #big enough
print(assult_clean.shape)
assult_clean.corr(numeric_only=True)

missing_clean = df2[df2['Incident Category']=="Missing Person"]
print(missing_clean.shape)
missing_clean.corr(numeric_only=True)

"""###Step 3: Model analysis: building and training the model

a. Multi Regression for the many features

b. Building off of the most promising correlations discovered during exploration
"""

#split the data into training and testing
trainset, testset = train_test_split(df2, test_size=0.25)

# make col names more usable
df2.rename(columns={'Incident Year': 'year', 'Day Number': 'day', 'Minutes Til Report': 'minutes', 'Incident Time Hour': 'hour'}, inplace=True)

# Model #1: Time to Report

# multi regression

# Goal: predicts how long it takes to file a report, knowing the
# day of week, time, and elevation at which crime occurred

model_df2 = smf.ols(formula="minutes ~ year+day+hour+Elevation", data=trainset)
fitted = model_df2.fit()
fitted.summary()

# Model #2: Assult reporting

# multi regression

# Goal: predicts how long it takes to file an assult crime report,
# given the time and elevation at which crime occurred

assult_clean.rename(columns={'Incident Year': 'year', 'Day Number': 'day', 'Minutes Til Report': 'minutes', 'Incident Time Hour': 'hour'}, inplace=True)
m_assult_clean = smf.ols(formula="minutes ~ Elevation+hour", data=assult_clean) #shoved entire dataset, small
fitted_assult_clean = m_assult_clean.fit()
fitted_assult_clean.summary()

# Model #2: Elevation prediction

# multi regression (not a simple line)

# Goal: predicts how much relative crime to expect at given elevation

m_elevation = smf.ols(formula="Incidents ~ Elevation", data=df_elevation)
fitted_elevation = m_elevation.fit()
fitted_elevation.summary()

"""###Step 4: Results

Model #1: Despite more promising results from the correlation matrix, there doesn't seem to be a meaningful correlation between time it takes to report and the day, time, and elevation. With an R-squared result of 0.106, it's not hopeless. Next steps would be remove features with highest p-values.

Model #2: This is an example of a non-correlation. R-squared is very low (0.012), the R-adjusted is negative, and p-values indicate that this is no better than random chance. This lead should be dropped.

Model #3: With an adjusted R-squared of 0.525 (low number of samples so using adjusted R instead), and favorable p-value and F-statistic, this is the winner of the bunch. There seems to be a correlation between crime incidents and elevation.

###Step 5:  Discussion and conclusion

Multi regression was chosen to try to use all the features. I learned that it is not always good to try to use all features. Instead, focus on just the most promising ones.

Some of the datasets ended up small so I resorted to training using the whole dataset. With more effort, more real data can be harvested from the master SFPD dataset.

Conclusions:

1) Free and unmaintained data is dirty - you're paying with your time to clean it.

2) Raw data is hides insights. Crime does not have very obvious patterns; if it did then it would be better controlled. Interesting and novel insights, however, can still be found so it is worth it to continue analyzing.
"""