# Author: Jack Connor
# Date Created: Spring 2020

"""
This is a python script that makes a scatter plot of T640 versus Partisol data with the following features:
    Data is grouped by whether or not a wildfire was occuring
    Wildfire data is red, data with no wildfire is blue
    Linear regressions are shown for both datasets, and the combined dataset
This script was designed to be used on Linux.
If run on Windows, this script may handle characters in text files in unexpected ways.
"""

# Import required packages.
import numpy as np
import pandas as pd
import df_funs as _
import matplotlib.pyplot as plt
from datetime import timedelta

# Set a directory that will be used to find files.
directory = "data//"

# Establish filenames for datafiles.
read_file_1 = 'T640_PM25_preDMS_DailyAvg.csv'
read_file_2 = 'T640_20190725_to_20200405_DailyAvg.csv'
read_file_3 = 'Partisol_20190323_to_20200405.csv'
read_file_4 = 'Filtered CalFire.csv'

# Establish boundaries for plots.
xlim = 30
ylim = 30

# Set up interpreters for the timestamps in the various files.
dateparser_1 = lambda x: pd.datetime.strptime(x, '%m/%d/%Y')
dateparser_2 = lambda x: pd.datetime.strptime(x, '%Y/%m/%d %H:%M')
pd.plotting.register_matplotlib_converters()

# Read in the first datafile. Delete rows with empty cells or repeated timestamps. Reindex dataframe.
data_1 = pd.read_csv(directory + read_file_1, parse_dates = ['Date'], date_parser = dateparser_1)
data_1.dropna(axis = 0, inplace = True)
data_1.drop_duplicates(subset = "Date", keep = 'first', inplace = True)
data_1.reset_index(inplace = True, drop = True)

# Read in the second datafile. Delete rows with empty cells or erroneous values or repeated timestamps. Reindex dataframe.
data_2 = pd.read_csv(directory + read_file_2, parse_dates = ['Date (LST)'], date_parser = dateparser_2)
data_2.dropna(axis = 0, inplace = True)
data_2.drop_duplicates(subset = "Date (LST)", keep = 'first', inplace = True)
data_2 = data_2[data_2['Value'] != -999]
data_2.reset_index(inplace = True, drop = True)

# Read in the third datafile. Delete rows with empty cells or erroneous values or repeated timestamps. Reindex dataframe.
data_3 = pd.read_csv(directory + read_file_3, parse_dates = ['Date (LST)'], date_parser = dateparser_2)
data_3.dropna(axis = 0, inplace = True)
data_3.drop_duplicates(subset = "Date (LST)", keep = 'first', inplace = True)
data_3 = data_3[data_3['Value'] != -999]
data_3.reset_index(inplace = True, drop = True)

# Copy and modify third dataframe.
partisol = data_3
partisol.rename(columns = {'Date (LST)' : 'Date'}, inplace = True)
partisol = partisol[["Date", "Value"]]

# Read in fifth datafile.
data_4 = pd.read_csv(directory + read_file_4, parse_dates = ['Date', 'End Date'],  date_parser = dateparser_1)

# Based on the known start and end dates of fires (data_4), create a list of all the dates in which wildfires were occuring. 
fire_dates = []
i = 0
for x in data_4["Date"]:
    StartDate = x
    EndDate = data_4.iloc[i][2]
    Date = StartDate
    while (EndDate - Date).days >= 0:
        if Date in fire_dates:
            Date = Date + timedelta(days=1)
        else:
            fire_dates += [Date]
            Date = Date + timedelta(days=1)
    i += 1

# Dataframes containing weekday and month were generated as an artifact of another script.
# While the weekday/month columns are not referenced, the dataframes themselves are referenced later in the script.
# Consequently the code has not been removed.

# Generate a T640 dataframe that has columns for weekday and month.
T640_Date = []
T640_Value = []
weekday = []
month = []
i = 0
for x in data_1['Date']:
    T640_Date += [x]
    T640_Value += [data_1.iloc[i][1]]
    weekday += [x.weekday()]
    month += [x.month]
    i += 1
i = 0
for x in data_2['Date (LST)']:
    T640_Date += [x]
    T640_Value += [data_2.iloc[i][3]]
    weekday += [x.weekday()]
    month += [x.month]
    i += 1
T640 = pd.DataFrame(data = T640_Date, columns = ["Date"])
T640.loc[:, ("Value")] = pd.Series(T640_Value)
T640.loc[:, ("weekday")] = pd.Series(weekday)
T640.loc[:, ("month")] = pd.Series(month)

# Generate a partisol dataframe that has columns for weekday and month.
weekday = []
month = []
for x in partisol["Date"]:
    weekday += [x.weekday()]
    month += [x.month]
partisol.insert(2, "weekday", weekday) 
partisol.insert(3, "month", month)

# Limit T640 and partisol dataframes to the timestamps that they share.
(T640, partisol, dates) = _.time_sync_2(T640, partisol)
T640.reset_index(inplace = True, drop = True)
partisol.reset_index(inplace = True, drop = True)

# Split dataframes into dates where fires were and were not occuring.
T640_Fire = T640[T640["Date"].isin(fire_dates)]
T640_NoFire = T640[~T640["Date"].isin(fire_dates)]
partisol_Fire = partisol[partisol["Date"].isin(fire_dates)]
partisol_NoFire = partisol[~partisol["Date"].isin(fire_dates)]

# Set the font size for the plots.
plt.rcParams['font.size'] = 20

# Create a string containing special characters for units to show on plot.
units = ' (' + r'$\rm \mu$' + 'g/m' + r'$^3$' + ')'

# Establish a figure.
fig, ax1 = plt.subplots( figsize = (20, 20), nrows = 1, ncols = 1)
plt.subplots_adjust(bottom = .17)

# Plot data where there was no fire in blue. Plot an associated linear regression.
ax1.plot(T640_NoFire["Value"], partisol_NoFire["Value"], "ob", label = "Days Without Fire")
_.plt_lin_reg_2(T640_NoFire["Value"], partisol_NoFire['Value'], ax1, '-b', .8*xlim,.72*ylim)
# Plot data where there was a fire in red. Plot an associated linear regression.
ax1.plot(T640_Fire["Value"], partisol_Fire["Value"], "or", label = "Fire Days")
_.plt_lin_reg_2(T640_Fire["Value"], partisol_Fire['Value'], ax1, '-r', .86*xlim, .46*ylim)
# Plot a linear regression for the combined dataset.
_.plt_lin_reg_2(T640["Value"], partisol['Value'], ax1, '-k', .925*xlim, .595*ylim)
# Establish axis limits, labels, and legend.
ax1.set_ylabel('Partisol PM' + r'$\rm _{2.5}$' + units)
ax1.set_xlim([0, xlim])
ax1.set_ylim([0, ylim])
ax1.legend(loc = 4)
ax1.set_xlabel('T640 PM' + r'$\rm _{2.5}$' + units)

# Show and save figure.
plt.show()
fig.savefig('Fire_Correlations.png')
