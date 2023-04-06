# Author: Jack Connor
# Date Created: Unknown

"""
This is a library that was made to assist with common operations on pandas DataFrames and basic data analysis tasks.
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def to_datetime(df, date):
    """
    This function converts a DataFrame date column to a list of datetimes.
    Args:
        df (pandas.DataFrame): DataFrame with a column containing timestamps registered with pandas as datetime objects
        date (str): name of the column containing the timestamps
    Returns:
        y (list): list of datetimes
        
    """
    y = [0]*len(df[date])
    i=0
    for x in df[date]:
        y[i] = x.to_pydatetime()
        i=i+1
    return(y)

def df_select(df, p, s):
    """
    Filter a dataframe to periods where a specified column contains a specified value.
    Args:
        df (pandas.DataFrame): DataFrame to filter
        p (str): parameter/column name to filter on
        s (str, float, int, bool): value to filter for
    Returns
        new_df (pandas.DataFrame): filtered DataFrame
    """
    new_df = df[df[p] == s]
    return(new_df)

def df_omit_zeros(df, v):
    """
    Omit rows from a DataFrame that contain any value less than or equal to zero in a specified column.
    Args:
        df (pandas.DataFrame): DataFrame to filter
        v (str): column name/parameter to filter on
    Returns:
        df_new (pandas.DataFrame): filtered DataFrame
    """
    df_new = df[df[v] > 0.0]
    return(df_new)

def df_floor(df, v, f):
    """
    Omit rows from a DataFrame that contain any value less than or equal to a specified value in a specified column.
    Args:
        df (pandas.DataFrame): DataFrame to filter
        v (str): column name/parameter to filter on
        f (int, float): threshold for filter
    Returns:
        df_new (pandas.DataFrame): filtered DataFrame
    """
    df_new = df[df[v] > f]
    return(df_new)

def time_sync(df_2, df_1):
    """
    Returns an array of values of df_2 that are synced with the timestamps of df_1.
    Where df_1 has a value for a particular timepoint, but df_2 does not, returns an NA value for that row of the output array.
    Where df_2 has a value for a particular timepoint, but df_1 does not, that value and timepoint are omitted from output array.
    Args:
        df_1 (pandas.DataFrame): first DataFrame
        df_2 (pandas.DataFrame): second DataFrame
    Returns:
        y (numpy.array): array containing df_2 values, but only at timestamps contained in df_1
    """
    dates = df_1["Date"]
    y = [0]*len(dates)
    i = 0
    for x in dates:
        instantaneous_df_2 = df_2[df_2["Date"] == x]
        value_2 = instantaneous_df_2.iloc[0][3]
        y[i] = value_2
        i = i+1
    y = np.array(y)
    return(y)

def time_sync_2(df_1, df_2):
    """
    Compares two dataframes and filters each to rows with timestamps shared by the two.
    Args:
        df_1 (pandas.DataFrame): DataFrame 1
        df_2 (pandas.DataFrame): DataFrame 2
    Returns:
        df_1_new (pandas.DataFrame): df_1 filtered to shared timestamps
        df_2_new (pandas.DataFrame): df_2 filtered to shared timestamps
        x (list): list of the timestamps shared by the two dataframes
    """
    df_1_new = df_1[df_1['Date'].isin(df_2['Date'])]
    df_2_new = df_2[df_2['Date'].isin(df_1['Date'])]
    x = to_datetime(df_1_new, "Date")
    return(df_1_new, df_2_new, x)

def conv_units(df, p, f):
    """
    Convert the units of a DataFrame column.
    Args:
        df (pandas.DataFrame): DataFrame input
        p (str): name of column to apply unit conversion to
        f (float): unit conversion factor
    Returns:
        y (np.array): array containing converted column values
    """
    y = [0]*len(df[p])
    i = 0
    for x in df[p]:
        y[i] = x*f
        i = i+1
    y = np.array(y)
    return(y)

def conv_units_2(df, f, date_index, value_index, Value = None):
    """
    Convert the units in a column of a DataFrame.
    Return a new DataFrame with the column in the converted units.
    Args:
        df (pandas.DataFrame): the input DataFrame
        f (float): the conversion factor
        date_index (int): index of the datetime column
        value_index (int): index of the column containing the values to convert
    Returns:
        new_df (pandas.DataFrame): new DataFrame containing columns for datetime and the converted value 
    """
    Value = list(df)[value_index]
    x = [0]*len(df['Date'])
    y = [0]*len(df['Date'])
    for i in range(0, len(df['Date'])):
        x[i] = df.iloc[i][date_index]
        y[i] = df.iloc[i][value_index]*f
    new_df = pd.DataFrame( data = np.array(y).T, columns = [Value] )
    new_df.loc[:,"Date"] = pd.Series(x)
    return(new_df)

def plt_lin_reg(x, y, ax, mf, norm_text_locx, norm_text_locy):
    """
    Plot a linear regression on a preexisting plot.
    Text associated with the regression is located by ratios relative to the data minima and maxima.
    Args:
        x (array-like): x values for the regression
        y (array-like): y values for the regression
        ax (matplotlib.pyplot.axes): preexisting plot object
        mf (str): string indicating marker format in matplotlib conventions
        norm_text_locx (float): ratio from 0 to 1 indicating where along the x axis to locate the regression text
        norm_text_locy (float): ratio from 0 to 1 indicating where along the y axis to locate the regression text
    Returns:
        Draws a regression line and prints associated R2 and linear equation on plot
    """
    m, b, r, p, se = stats.linregress(x, y)
    x_r = [min(x), max(x)]
    y_r = [m*min(x)+b, m*max(x)+b]
    rs = str(round(r**2, 2))
    m_ = str(round(m, 2))
    b_ = np.around(b).astype('str')
    ax.plot(x_r, y_r, mf)
    ax.text(
            min(x)+norm_text_locx*(max(x)-min(x)),
            (m*min(x)+b)+norm_text_locy*((m*max(x)+b)-(m*min(x)+b)),
            'y = '+ m_ +'x + ' + b_ + '\n' + 'r' + r'$^2$' + ' = ' + rs,
            horizontalalignment = 'center'
            )

def plt_lin_reg_2(x, y, ax, mf, text_locx, text_locy):
    """
    Plot a linear regression on a preexisting plot.
    Text associated with the regression is located by absolute x and y values.
    Args:
        x (array-like): x values for the regression
        y (array-like): y values for the regression
        ax (matplotlib.pyplot.axes): preexisting plot object
        mf (str): string indicating marker format in matplotlib conventions
        text_locx (float): x value of the regression text location
        text_locy (float): y value of the regression text location 
    Returns:
        Draws a regression line and prints associated R2 and linear equation on plot
    """
    m, b, r, p, se = stats.linregress(x, y)
    x_r = [min(x), max(x)]
    y_r = [m*min(x)+b, m*max(x)+b]
    rs = str(round(r**2, 2))
    m_ = str(round(m, 2))
    b_ = np.around(b).astype('str')
    ax.plot(x_r, y_r, mf)
    ax.text(
            text_locx,
            text_locy,
            'y = '+ m_ +'x + ' + b_ + '\n' + 'r' + r'$^2$' + ' = ' + rs,
            c = mf[1],
            horizontalalignment = 'center' 
            )

def plt_line_reg(x, y, ax, mf):
    """
    Plot a linear regression on a preexisting plot. Do not display regression information text.
    Args:
        x (array-like): x values for the regression
        y (array-like): y values for the regression
        ax (matplotlib.pyplot.axes): preexisting plot object
        mf (str): string indicating marker format in matplotlib conventions
    Returns:
        Draws a regression line
    """
    m, b, r, p, se = stats.linregress(x, y)
    x_r = [min(x), max(x)]
    y_r = [m*min(x)+b, m*max(x)+b]
    rs = np.around(r**2, 2).astype('str')
    m_ = np.around(m, 2).astype('str')
    b_ = np.around(b, 2).astype('str')
    ax.plot(x_r, y_r, mf)

def plt_lin_reg_y_int(x, y, ax, mf, text_locx, text_locy):
    """
    Plot a linear regression on a preexisting plot.
    Plots regression from y intercept to x maximum.
    Text associated with the regression is located by absolute x and y values.
    Args:
        x (array-like): x values for the regression
        y (array-like): y values for the regression
        ax (matplotlib.pyplot.axes): preexisting plot object
        mf (str): string indicating marker format in matplotlib conventions
        text_locx (float): x value of the regression text location
        text_locy (float): y value of the regression text location 
    Returns:
        Draws a regression line and prints associated R2 and linear equation on plot
    """
    m, b, r, p, se = stats.linregress(x, y)
    x_r = [0, max(x)]
    y_r = [m*0+b, m*max(x)+b]
    rs = str(round(r**2, 2))
    m_ = str(round(m, 2))
    b_ = np.around(b).astype('str')
    ax.plot(x_r, y_r, mf)
    ax.text(
            text_locx,
            text_locy,
            'y = '+ m_ +'x + ' + b_ + '\n' + 'r' + r'$^2$' + ' = ' + rs,
            c = 'k',
            horizontalalignment = 'center'
            )
