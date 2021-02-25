# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------- #
# "LMT opacity library". Afternoon example tau_per_year_afternoon.py
# Example. Tau per year averaged per month in period 2013-2020
#
# Marcial Becerril, @ May 2020
# Latest Revision: Feb 2021, 00:00 GMT-6
#
# For all kind of problems, requests of enhancements and bug reports, please
# write to me at:
#
# mbecerrilt92@gmail.com
# mbecerrilt@inaoep.mx
#
# --------------------------------------------------------------------------------- #

import numpy as np
from matplotlib.pyplot import *
import matplotlib.dates as md

# Latex format
rc('text', usetex=True)
rcParams.update({
    "text.usetex": True,
    "font.size": 20,
    "font.family": "serif"})

import pandas as pd

# Import tau library
from tau_lmt import *
tau = tau_lmt()


months_by_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


# Defining the period of hours averaged per day per month
months = np.array([[12,13,14,15,16,17,18],      # January
                  [12,13,14,15,16,17,18],       # February
                  [12,13,14,15,16,17,18],       # March
                  [12,13,14,15,16,17,18,19],    # April
                  [12,13,14,15,16,17,18,19,20], # May
                  [12,13,14,15,16,17,18,19,20], # June
                  [12,13,14,15,16,17,18,19,20], # July
                  [12,13,14,15,16,17,18,19,20], # August
                  [12,13,14,15,16,17,18,19],    # September
                  [12,13,14,15,16,17,18,19],    # October
                  [12,13,14,15,16,17,18],       # November
                  [12,13,14,15,16,17,18]])      # December

# To some months we add 30 min extra
# Example:
# If months[0] = [12, 13, 14] and
#    mask_30min = [True, True]
# The averaging period is from 11:30 - 14:30
mask_30min = np.array([[False, False], # January
                [False, True],         # February
                [False, True],         # March
                [False, True],         # April
                [False, False],        # May
                [False, False],        # June
                [False, False],        # July
                [False, False],        # August
                [False, True],         # September
                [False, False],        # October
                [False, False],        # November
                [False, False]])       # December

# Years to average
years = ['2013','2014','2015','2016','2017','2018','2019','2020']

# Get data per year
for year in years:
    # Define dataframe to storage year data
    data = pd.DataFrame()
    # Averaging data per month
    for m in range(12):

        # Create the filter chain for hours which belong to the afternoon
        hrs_string = ''
        for hr in months[m]:
            hrs_string = hrs_string + ','+str(hr)
        hrs_string = hrs_string[1:]

        # Apply filter
        time_afternoon = tau.filter(tau.raw_data, '-yr '+year+' -mn '+str(m+1)+' -hr '+hrs_string)

        # Concatenating data for those additional 30 minutes
        # ===================================================
        # At the beginning
        if mask_30min[m][0]:
            # Get hour and minutes to average
            hr_corr = months[m][0]-1
            min_corr = np.arange(30,60)

            # Create the filter chain for minutes, from 30-59
            mins_string = ''
            for mt in min_corr:
                mins_string = mins_string + ','+str(mt)
            mins_string = mins_string[1:]

            # Get data missing (before 30 min)
            corr = tau.filter(tau.raw_data, '-yr '+year+' -mn '+str(m+1)+' -hr '+str(hr_corr)+' -mt '+mins_string)

            # Apply correction
            time_afternoon = pd.concat([corr, time_afternoon])

        # At the end
        if mask_30min[m][1]:
            # Get hour and minutes to average
            hr_corr = months[m][-1]+1
            min_corr = np.arange(30)

            # Create the filter chain for minutes, from 00-29
            mins_string = ''
            for mt in min_corr:
                mins_string = mins_string + ','+str(mt)
            mins_string = mins_string[1:]

            # Get data missing (after 30 min)
            corr = tau.filter(tau.raw_data, '-yr '+year+' -mn '+str(m+1)+' -hr '+str(hr_corr)+' -mt '+mins_string)

            # Apply correction
            time_afternoon = pd.concat([time_afternoon, corr])

        # Concatenate data
        data = pd.concat([data, time_afternoon])

    # Get statistics averaging by month (-mn 1)
    stat = tau.statistics_sample(data, '-mn 1', verbose=False)
    # Create csv file
    #stat.to_csv(year+'_afternoon.csv', index=False)

    # Create figure and plot data averaged by month (in afternoon hours) per year
    figs = subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
    tau.tau_plotter_hughes_format(stat, figs, show_limits=True)

    axes = figs[1]
    month_lab = months_by_name[:len(data)]
    if year == '2013':
        month_lab = months_by_name[5:]
    axes.set_xticklabels(month_lab)
    axes.set_title('Afternoon [12:00 pm - dusk] '+year)

