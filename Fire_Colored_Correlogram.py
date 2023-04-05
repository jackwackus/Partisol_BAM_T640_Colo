# Author: Jack Connor
# Date Created: Spring 2020

"""
This is a python script that makes a correlogram with the following features:
    3x3 - from left to right and top to bottom - T640, BAM, Partisol
    Plots are colored by whether or not a nearby wildfire was occuring on the day the data was collected.
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
directory = "/mnt/f/f_documents/data/concord colo//"

# Establish filenames for datafiles.
read_file_1 = 'T640_PM25_preDMS_DailyAvg.csv'
read_file_2 = 'T640_20190725_to_20200405_DailyAvg.csv'
read_file_3 = 'Partisol_20190323_to_20200405.csv'
read_file_4 = 'BAM_PM25_20190323_to_20200405.csv'
read_file_5 = 'Filtered CalFire.csv'

# Establish boundaries for plots.
xlim = 30
ylim = 30

# Establish parameters for locating regression information on plots.
# These are structured as ratios that will be multiplied by axis bounds.
# Two sets of regression locators are defined since regressions will be run for fire and no-fire days.
rx = .27
ry = .75
r_x = .74
r_y = .01

# Set up interpreters for the timestamps in the various files.
dateparser_1 = lambda x: pd.datetime.strptime(x, '%m/%d/%Y')
dateparser_2 = lambda x: pd.datetime.strptime(x, '%Y/%m/%d %H:%M')
dateparser_3 = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %H:%M')
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

# Read in the fourth datafile. Delete rows with empty cells or erroneous values or repeated timestamps. Reindex dataframe.
data_4 = pd.read_csv(directory + read_file_4, parse_dates = ['Date (LST)'], date_parser = dateparser_3)
data_4.dropna(axis = 0, inplace = True)
data_4.drop_duplicates(subset = "Date (LST)", keep = 'first', inplace = True)
data_4 = data_4[data_4['Value'] != -999]
data_4.reset_index(inplace = True, drop = True)

# Copy and modify fourth dataframe.
BAM = data_4
BAM.rename(columns = {'Date (LST)' : 'Date'}, inplace = True)
BAM = BAM[["Date", "Value"]]

# Read in fifth datafile.
data_5 = pd.read_csv(directory + read_file_5, parse_dates = ['Date', 'End Date'],  date_parser = dateparser_1)

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
#print(partisol)

# Generate a BAM dataframe that has columns for weekday and month.
weekday = []
month = []
for x in BAM["Date"]:
    weekday += [x.weekday()]
    month += [x.month]
BAM.insert(2, "weekday", weekday) 
BAM.insert(3, "month", month)

# Based on the known start and end dates of fires (data_5), create a list of all the dates in which wildfires were occuring. 
fire_dates = []
i = 0
for x in data_5["Date"]:
    StartDate = x
    EndDate = data_5.iloc[i][2]
    Date = StartDate
    while (EndDate - Date).days >= 0:
        if Date in fire_dates:
            Date = Date + timedelta(days=1)
        else:
            fire_dates += [Date]
            Date = Date + timedelta(days=1)
    i += 1

# Limit T640, partisol, and BAM dataframes to the timestamps that they all share.
(T640, partisol, dates) = _.time_sync_2(T640, partisol)
(BAM, partisol, dates) = _.time_sync_2(BAM, partisol)
(BAM, T640, dates) = _.time_sync_2(BAM, T640)
T640.reset_index(inplace = True, drop = True)
partisol.reset_index(inplace = True, drop = True)
BAM.reset_index(inplace = True, drop = True)

# Split dataframes into dates where fires were and were not occuring.
T640_Fire = T640[T640["Date"].isin(fire_dates)]
T640_NoFire = T640[~T640["Date"].isin(fire_dates)]
BAM_Fire = BAM[BAM["Date"].isin(fire_dates)]
BAM_NoFire = BAM[~BAM["Date"].isin(fire_dates)]
partisol_Fire = partisol[partisol["Date"].isin(fire_dates)]
partisol_NoFire = partisol[~partisol["Date"].isin(fire_dates)]

# Sort relevant values so they can be used in a histogram.
T640.sort_values(by = "Value", axis = 0, inplace = True) 
T640.reset_index(inplace = True, drop = True)
T640_hist = []
BAM.sort_values(by = "Value", axis = 0, inplace = True) 
BAM.reset_index(inplace = True, drop = True)
BAM_hist = []
partisol.sort_values(by = "Value", axis = 0, inplace = True) 
partisol.reset_index(inplace = True, drop = True)
partisol_hist = []

# Group data so that loops can be used to generate plots.
data = [T640['Value'], BAM['Value'], partisol['Value']]
data_Fire = [T640_Fire['Value'], BAM_Fire['Value'], partisol_Fire['Value']]
data_NoFire = [T640_NoFire['Value'], BAM_NoFire['Value'], partisol_NoFire['Value']]

# Put labels into a list so that they can be pulled in the plotting loop.
labels = ["T640", "BAM", "Partisol"]

# Set the font size for the plots.
plt.rcParams['font.size'] = 20

# Create the figure with nine subplots. Format and name the subplots.
fig, [[ax1, ax2, ax3], [ax4, ax5, ax6], [ax7, ax8, ax9]] = plt.subplots( figsize = (20, 20), nrows = 3, ncols = 3)
axes = [[ax1, ax2, ax3], [ax4, ax5, ax6], [ax7, ax8, ax9]]

# Loop through the three rows of the figure.
for i in range(0,3):
    # Loop through the three columns of the figure.
    for j in range(0,3):
        # When on the diagonal, plot a histogram.
        if i == j:
            # Use matplotlib's built in histogram function. Specify the two datasets, 10 bins, and a bin range of 0 to 30.
            # Specify black and red coloring for the respective datasets. Stack the two datasets.
            axes[i][j].hist([data_NoFire[i], data_Fire[i]], bins = 10, range =  (0, 30), stacked = True, color = ["k", "r"]) 
            axes[i][j].set_xlim([0, xlim])
            axes[i][j].set_ylim([0, 47])
        # When not on the diagonal, plot scatter plots.
        else:
            # Plot fire and no fire data separately with separate colors and linear regressions.
            axes[i][j].plot(data_NoFire[j], data_NoFire[i], 'ok')
            _.plt_lin_reg_2(data_NoFire[j], data_NoFire[i], axes[i][j], '-k', rx*xlim, ry*ylim)
            axes[i][j].plot(data_Fire[j], data_Fire[i], 'or')
            _.plt_lin_reg_2(data_Fire[j], data_Fire[i], axes[i][j], '-r', r_x*xlim, r_y*ylim)
            axes[i][j].set_xlim([0, xlim])
            axes[i][j].set_ylim([0, ylim])
        # Apply x axis labels to the bottom row of subplots.
        if i == 2:
            axes[i][j].set_xlabel(labels[j])
        # Apply y axis labels to the left column of subplots.
        if j == 0:
            axes[i][j].set_ylabel(labels[i])
    j += 1
i += 1

# Show and save figure.
plt.show()
fig.savefig('/mnt/f/f_documents/data/concord colo/figures/Fire Correlogram.png')
