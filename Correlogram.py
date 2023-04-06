# Author: Jack Connor
# Date Created: Spring 2020

"""
This is a python script that makes a correlogram with the following features:
    3x3 - from left to right and top to bottom - T640, BAM, Partisol
    Plots are colored by x-axis value to visually enhance comparisons between and within columns
This script was designed to be used on Linux.
If run on Windows, this script may handle characters in text files in unexpected ways.
"""

# Import required packages.
import numpy as np
import pandas as pd
import df_funs as _
import matplotlib.pyplot as plt

# Set a directory that will be used to find files.
directory = "data//"

# Establish filenames for datafiles.
read_file_1 = 'T640_PM25_preDMS_DailyAvg.csv'
read_file_2 = 'T640_20190725_to_20200405_DailyAvg.csv'
read_file_3 = 'Partisol_20190323_to_20200405.csv'
read_file_4 = 'BAM_PM25_20190323_to_20200405.csv'

# Establish boundaries for plots.
xlim = 30
ylim = 30

# Establish parameters for locating regression information on plots.
# These are structured as ratios that will be multiplied by axis bounds.
rx = .27
ry = .75

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

# Limit T640, partisol, and BAM dataframes to the timestamps that they all share.
(T640, partisol, dates) = _.time_sync_2(T640, partisol)
(BAM, partisol, dates) = _.time_sync_2(BAM, partisol)
(BAM, T640, dates) = _.time_sync_2(BAM, T640)
T640.reset_index(inplace = True, drop = True)
partisol.reset_index(inplace = True, drop = True)
BAM.reset_index(inplace = True, drop = True)

# Sort relevant values so they can be used in a histogram.
T640_hist_df = T640.sort_values(by = "Value", axis = 0) 
T640_hist_df.reset_index(inplace = True, drop = True)
T640_hist = []
BAM_hist_df = BAM.sort_values(by = "Value", axis = 0) 
BAM_hist_df.reset_index(inplace = True, drop = True)
BAM_hist = []
partisol_hist_df = partisol.sort_values(by = "Value", axis = 0) 
partisol_hist_df.reset_index(inplace = True, drop = True)
partisol_hist = []

# Group data so that loops can be used to generate plots.
data = [T640['Value'], BAM['Value'], partisol['Value']]
data_hists = [T640_hist_df['Value'], BAM_hist_df['Value'], partisol_hist_df['Value']]
hists = [T640_hist, BAM_hist, partisol_hist]

# Populate lists defining histograms for each instrument.
# The final lists contain quantities for each bin corresponding to the number of datapoints within that bin.
j = 0
for hist in hists:
    # For each instrument, initialize a list containing 0 for every bin.
    for y in np.arange(3.0, 33.0, 3.0):
        hist += [0]
    # For each instrument, go through the sorted data. While the data is less than or equal to the value of the current bin (starting at the lowest),
    # add 1 to the quantity for that bin. Once the data exceeds the value of current bin, move to the next bin.
    # Proceed until all data has been counted.
    i = 0
    for x in data_hists[j]:
        if x < np.arange(3.0, 33.0, 3.0)[i]:
            hist[i] += 1
        else:
            while x >= np.arange(3.0, 33.0, 3.0)[i]:
                i += 1
            hist[i] += 1
    j += 1

# Establish values for the x-axis of the histogram. Use the center of each bin.
hist_x = np.arange(1.5, 31.5, 3)
        
# Put labels into a list so that they can be pulled in the plotting loop.
labels = ["T640", "BAM", "Partisol"]

# Establish a colormap based on the expected range of the data (0 to 30).
colors_1 = plt.cm.get_cmap('jet', 30)

# Establish a colormap for the histogram (containing 10 bins) using the same colorscale as the other colormap.
# Colors need to be formatted as a list for the bar graph function that will be used.
cm = plt.cm.get_cmap('jet', 10)
colors_2 = []
for i in range(0,10):
    colors_2 += [cm(i)]

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
            # Plot each bar individually with quantity and color as determined above.
            for k in range(0,10):
                axes[i][j].bar(hist_x[k], hists[j][k], width = 3, color = colors_2[k]) 
            # Set axis bounds.
            axes[i][j].set_xlim([0, xlim])
            axes[i][j].set_ylim([0, 47])
        # When not on diagonal, plot colored scatter plots. 
        else:
            # Individually plot each point and color it by its value.
            for k in range(0, len(data[j])):
                axes[i][j].plot(data[j].iloc[k], data[i].iloc[k], 'o', c = colors_1(int(data[j].iloc[k])))
            # Carry out a linear regression and plot it.
            _.plt_lin_reg_2(data[j], data[i], axes[i][j], '-k', rx*xlim, ry*ylim)
            # Set axis bounds.
            axes[i][j].set_xlim([0, xlim])
            axes[i][j].set_ylim([0, ylim])
        # If on the bottom row, apply x labels.
        if i == 2:
            axes[i][j].set_xlabel(labels[j])
        # If on the left column, apply y labels.
        if j == 0:
            axes[i][j].set_ylabel(labels[i])
    j += 1
i += 1

# Show and save plot.
plt.show()
fig.savefig('Correlogram.png')
