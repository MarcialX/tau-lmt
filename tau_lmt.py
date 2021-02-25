# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------- #
# "LMT opacity library" tau_lmt.py
# Tools to get and analyse the LMT opacity along the period 2013-2020
#
# Marcial Becerril, @ May 2020
# Latest Revision: Feb 2021, 21:57 GMT-6
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

import pandas as pd

# Interactive plots
ion()

# Path of the tau lmt file
FILE_TAU_PATH = "./data/Tau_LMT_Site_(2013-06-01)_(2020-03-21).csv"

# MISCELLANEOUS FUNCTIONS
# Printing Messages
def print_msg(msg, alarm_type):
    """
        Messages
        Parameters
        ----------
        msg : string
            Message to show
        alarm_type : string
            Kind of message: info, ok, warning, error or verb
        ----------
    """
    # Color alarm
    color_alarms = ['\033[94m', '\033[92m', '\033[93m', '\033[91m', '']
    # Types of alarms
    alarms = ['info', 'ok', 'warning', 'error', 'verb']
    for i, alarm in enumerate(alarms):
        if alarm == alarm_type:
            print (color_alarms[i] + msg + '\033[0m')
            return

    return color_alarms[-1] + "ERROR! Type of message not recognized: ", alarm_type, '\033[0m'


class tau_lmt():
    """
        Messages
        Parameters
        ----------
        path : string
            Opacity data path
        *args : additional arguments
        **kargs : additional keywords (for verbose)
        ----------
    """
    def __init__(self, path=FILE_TAU_PATH, *args, **kwargs):
        # Check for verbose
        verbose = kwargs.pop('verbose', None)

        # Initiating the class, the tau file is loaded
        print_msg('Loading tau file...', 'info')
        self.raw_data = pd.read_csv(path, names=['Date', 'Time', 'Tau'], header=None)
        # Unifying time columns
        self.raw_data['Date'] = self.raw_data['Date']+'T'+self.raw_data['Time']
        self.raw_data['Date'] = pd.to_datetime(self.raw_data['Date'])
        self.raw_data.drop('Time', inplace=True, axis=1)

        # Night definition. From 21:00 pm - 8:00 am
        self.night = np.array([21,22,23,0,1,2,3,4,5,6,7,8])

        # Number of points
        self.n_points = len(self.raw_data.index)

        # Limits of tau list
        self.first_date = self.raw_data['Date'][0]
        self.last_date = self.raw_data['Date'][self.n_points-1]

        if verbose:
            print_msg('Tau file: '+FILE_TAU_PATH, 'verb')
            print_msg('No. of points: '+str(self.n_points), 'verb')
            print_msg('Data from: '+str(self.first_date) + ' to: '+str(self.last_date), 'verb')
        print_msg('File loaded!', 'ok')


    def check_availability(self, date_time):
        """
            Check if date is available on database
            Parameters
            ----------
            date_time : datetime
                Date to check whether is available or not on database
            ----------
        """
        # Check min limit
        if (date_time-self.first_date).total_seconds()/60. < 0:
            date_time = self.first_date
            print_msg('Minimum available date: '+str(self.first_date), 'warning')
            print_msg('Date assigned: '+str(self.first_date), 'info')
        # Check max limit
        elif (date_time-self.last_date).total_seconds()/60 > 0:
            date_time = self.last_date
            print_msg('Maximum available date: '+str(self.last_date), 'warning')
            print_msg('Date assigned: '+str(self.last_date), 'info')

        return date_time


    def time_span(self, from_date, to_date, **kwargs):
        """
            Choose a time span
            Parameters
            ----------
            from_date : datetime
                From date
            to_date : datetime
                To date
            **kwargs : additional keywords (for verbose)
            ----------
        """
        # Add verbose
        verbose = kwargs.pop('verbose', None)

        from_date = pd.Timestamp(from_date)
        to_date = pd.Timestamp(to_date)

        if (to_date - from_date).total_seconds()/60. < 0:
            print_msg('Period is not valid, the first date has to be before the last date', 'error')
            return

        from_date = self.check_availability(from_date)
        to_date = self.check_availability(to_date)

        span_sample = self.raw_data[
            (self.raw_data['Date'] > from_date ) &
            (self.raw_data['Date'] < to_date)
        ]

        if verbose:
            n_points = len(span_sample.index)
            print_msg('No. of sample points: '+str(n_points), 'verb')
            if n_points > 0:
                print_msg('Data from: '+ str(span_sample.iloc[0].Date) + ' to: ' + str(span_sample.iloc[n_points-1].Date), 'verb')

        return span_sample


    def validate_dates(self, array_date, field):
        """
            Validate dates
            Parameters
            ----------
            array_date : datetime's array
                Array of datetimes to validate
            field : string
                Temporal scale selected: t, yr, mn, dy, hr, mt
            ----------
        """
        for item in array_date:
            if field == 't':
                if item < 0:
                    print_msg('Tau value not valid! It will be ignored', 'error')
                    array_date.remove(item)
            elif field == 'yr':
                if item < 0:
                    print_msg('Year not valid! It will be ignored', 'error')
                    array_date.remove(item)
            elif field == 'mn':
                if item < 1 or item > 12:
                    print_msg('Month not valid! It will be ignored', 'error')
                    array_date.remove(item)
            elif field == 'dy':
                if item < 1 or item > 31:
                    print_msg('Day not valid! It will be ignored', 'error')
                    array_date.remove(item)
            elif field == 'hr':
                if item < 0 or item > 23:
                    print_msg('Hour not valid! It will be ignored', 'error')
                    array_date.remove(item)
            elif field == 'mt':
                if item < 0 or item > 59:
                    print_msg('Minute not valid! It will be ignored', 'error')
                    array_date.remove(item)

        return array_date


    def filter(self, sample, filter_chain, **kwargs):
        """
            To filter the data
            Parameters
            ----------
            sample : 
                Datetime data sample
            filter_chain : string
                Filter chain: 
                Example:-yr 2018 -mn 12 -dy -25
            **kwargs : additional keywords (for verbose)
            ----------
        """
        # Add verbose
        verbose = kwargs.pop('verbose', None)

        # yr:    Filter per year
        # mn:    Filter per month
        # dy:    Filter per day
        # hr:    Filter per hour
        # mt:    Filter per minute
        # ng:    Filter per nights

        ts = []
        yrs = []
        mns = []
        dys = []
        hrs = []
        mts = []
        night = False

        # Auxiliar variables
        cmd = ''
        data = ''
        val = ''

        # Get filter values
        for i, char in enumerate(filter_chain):
            if char == '-':
                flag_cmd = True
                cmd = ''
            elif char == ' ' and flag_cmd:
                flag_cmd = False
            elif flag_cmd:
                cmd = cmd + char
            # Look for years
            elif cmd == 'yr' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        yrs.append(int(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        yrs.append(int(val))
            # Look for months
            elif cmd == 'mn' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        mns.append(int(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        mns.append(int(val))
            # Look for days
            elif cmd == 'dy' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        dys.append(int(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        dys.append(int(val))
            # Look for hours
            elif cmd == 'hr' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        hrs.append(int(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        hrs.append(int(val))
            # Look for minutes
            elif cmd == 'mt' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        mts.append(int(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        mts.append(int(val))
            # Look for tau
            elif cmd == 't' and not flag_cmd:
                if char == ',' or char == ' ':
                    try:
                        ts.append(float(val))
                    except:
                        pass
                    val = ''
                else:
                    val = val + char
                    if i == len(filter_chain)-1:
                        ts.append(float(val))
            # Look for the nights
            elif cmd == 'ng' and not flag_cmd:
                night = True

            if i == len(filter_chain)-1:
                if cmd == 'ng':
                    night = True

        ts = self.validate_dates(ts, 't')
        yrs = self.validate_dates(yrs, 'yr')
        mns = self.validate_dates(mns, 'mn')
        dys = self.validate_dates(dys, 'dy')
        hrs = self.validate_dates(hrs, 'hr')
        mts = self.validate_dates(mts, 'mt')

        # Applying the filters
        # For tau
        if ts:
            t = np.min(ts)
            mask_tau = sample['Tau'].values < t
            sample = sample[mask_tau]
        # For years
        if yrs:
            mask_year = np.in1d(pd.DatetimeIndex(sample['Date']).year.values , yrs)
            sample = sample[mask_year]
        # For months
        if mns:
            mask_month = np.in1d(pd.DatetimeIndex(sample['Date']).month.values , mns)
            sample = sample[mask_month]
        # For days
        if dys:
            mask_day = np.in1d(pd.DatetimeIndex(sample['Date']).day.values , dys)
            sample = sample[mask_day]
        # For hours
        if night:  # Defining nights
            hrs = self.night
            mask_hour = np.in1d(pd.DatetimeIndex(sample['Date']).hour.values , hrs)
            sample = sample[mask_hour]
        elif hrs:
            mask_hour = np.in1d(pd.DatetimeIndex(sample['Date']).hour.values , hrs)
            sample = sample[mask_hour]
        # For minute
        if mts:
            mask_minute = np.in1d(pd.DatetimeIndex(sample['Date']).minute.values , mts)
            sample = sample[mask_minute]

        if verbose:
            n_points = len(sample.index)
            print_msg('No. of sample points: '+str(n_points), 'verb')
            if n_points > 0:
                print_msg('Data from: '+ str(sample.iloc[0].Date) + ' to: ' + str(sample.iloc[n_points-1].Date), 'verb')

        return sample


    def statistics_sample(self, sample, group_string, **kwargs):
        """
            To get the statistics
            Parameters
            ----------
            sample : 
                Datetime data sample
            group_string : string
                Time scale to get the statistic
            **kwargs : additional keywords (for verbose)
            ----------
        """
        # Add verbose
        verbose = kwargs.pop('verbose', None)

        # Decode the string instructions
        flag_cmd = False
        flag_value = False
        val = ''
        for i, char in enumerate(group_string):
            if char == '-':
                flag_value = True
                flag_cmd = True
                cmd = ''
            elif char == ' ' and flag_cmd:
                flag_cmd = False
            elif char == ' ' and flag_value:
                flag_value = False
                flag_cmd = False
                break
            elif flag_cmd:
                cmd = cmd + char
            # Read the value of the command
            elif flag_value and not flag_cmd:
                val = val + char

        time_groups = ['yr', 'mn', 'dy', 'ng', 'hr', 'mt']

        # Check the command is valid
        if not cmd in time_groups:
            print_msg('Command: '+ cmd +' is not valid', 'error')
            return

        # Check that value is valid
        try:
            value = int(val)
        except:
            print_msg('Value: '+ val +' is not valid', 'error')
            return

        # Grouping year
        n_points = len(sample.index)

        # Date limits
        init_date = sample['Date'].iloc[0]
        end_date = sample['Date'].iloc[n_points-1]

        # Create data frame to store the stats
        rows_data_stat = []

        # Y E A R S
        if cmd == 'yr':
            # Number of days to read
            init_yr = init_date.year
            end_yr = end_date.year

            # Range of dates with an increasing factor of one day
            yrs = np.arange(init_yr, end_yr+1, 1)

            # Initial date mask
            # Step in months
            delta = pd.DateOffset(years=value)
            # Definition of one month
            one_year = pd.DateOffset(years=1)

            year_array_movil = sample[
                (sample['Date'] >= init_date ) &
                (sample['Date'] <= init_date+delta )
            ]

            date_mask = pd.DatetimeIndex(year_array_movil['Date'])

            # Auxiliar variables
            cnc_year = []
            cnt_year = 0
            trigger_year = False

            for yr in yrs:
                # Get year mask
                mask = np.in1d(date_mask.year.values , yr)

                # Trigger the counting
                if np.count_nonzero(mask) > 0:
                    trigger_year = True

                # Starting the day adquisition
                if trigger_year:

                    cnt_year = cnt_year + 1
                    cnc_year.append(yr)

                    # Averaging val samples
                    if cnt_year == value or yr == yrs[-1]:
                        mask = np.in1d(date_mask.year.values , cnc_year)
                        year_sample = year_array_movil[mask]

                        cnt_year = 0
                        cnc_year = []

                        if np.count_nonzero(mask) > 0:
                            mg = year_sample.describe().values.flatten()
                            cols_data = {}
                            cols_data.update({'Date': init_date, 'tau_count':mg[0], 'tau_mean':mg[1],
                                      'tau_std': mg[2], 'tau_25':mg[4], 'tau_50':mg[5], 'tau_75':mg[6], 'tau_max':mg[7],
                                      'tau_min': mg[3]
                                     })
                            rows_data_stat.append(cols_data)
                            if verbose:
                                print (year_sample.describe())
                        else:
                            if verbose:
                                print_msg('Empty span', 'warning')

                        # Re-define the sample size and boundaries
                        year_array_movil = sample[
                            (sample['Date'] >= init_date ) &
                            (sample['Date'] <= init_date+delta )
                        ]

                        # Updating the boundaries
                        init_date = init_date + delta

                        date_mask = pd.DatetimeIndex(year_array_movil['Date'])
        # M O N T H S
        elif cmd == 'mn':
            # Number of days to read
            nummonths = (end_date.year - init_date.year) * 12 + (end_date.month - init_date.month) + 1

            # Range of dates with an increasing factor of one day
            mns = []
            mn_count = init_date.month
            for i in range(nummonths):
                if mn_count > 12:
                    mn_count = 1
                mns.append(mn_count)
                mn_count += 1
            mns = np.array(mns)

            # Initial date mask
            # Step in months
            delta = pd.DateOffset(months=value)
            # Definition of one month
            one_month = pd.DateOffset(months=1)

            month_array_movil = sample[
                (sample['Date'] >= init_date-one_month ) &
                (sample['Date'] <= init_date+delta+one_month)
            ]

            date_mask = pd.DatetimeIndex(month_array_movil['Date'])

            # Auxiliar variables
            cnc_month = []
            cnt_month = 0
            trigger_month = False

            for i, mn in enumerate(mns):
                # Get month and mask
                mask = np.in1d(date_mask.month.values , mn)

                # Trigger the counting
                if np.count_nonzero(mask) > 0:
                    trigger_month = True

                # Starting the month adquisition
                if trigger_month:

                    cnt_month = cnt_month + 1
                    cnc_month.append(mn)

                    # Averaging val samples
                    if cnt_month == value or i == len(mns)-1:
                        mask = np.in1d(date_mask.month.values , cnc_month)
                        month_sample = month_array_movil[mask]

                        cnt_month = 0
                        cnc_month = []

                        if np.count_nonzero(mask) > 0:
                            print (month_sample['Date'].iloc[0], month_sample['Date'].iloc[len(month_sample.index)-1])
                            mg = month_sample.describe().values.flatten()
                            cols_data = {}
                            cols_data.update({'Date': init_date, 'tau_count':mg[0], 'tau_mean':mg[1],
                                      'tau_std': mg[2], 'tau_25':mg[4], 'tau_50':mg[5], 'tau_75':mg[6], 'tau_max':mg[7],
                                      'tau_min': mg[3]
                                     })
                            rows_data_stat.append(cols_data)
                            if verbose:
                                print (month_sample.describe())

                        else:
                            if verbose:
                                print_msg('Empty span', 'warning')

                        # Re-define the sample size and boundaries
                        month_array_movil = sample[
                            (sample['Date'] >= init_date-one_month ) &
                            (sample['Date'] <= init_date+delta+one_month)
                        ]

                        # Updating the boundaries
                        init_date = init_date + delta

                        date_mask = pd.DatetimeIndex(month_array_movil['Date'])

        # D A Y S
        elif cmd == 'dy':
            # Number of days to read
            numdays = (end_date-init_date).days

            # Range of dates with an increasing factor of one day
            dys = [init_date + pd.Timedelta(days=x) for x in range(numdays)]

            # Initial date mask
            # Step in days
            delta = pd.Timedelta(days=value)
            # Definition of one day
            one_day = pd.Timedelta(days=1)

            day_array_movil = sample[
                (sample['Date'] >= init_date-one_day ) &
                (sample['Date'] <= init_date+delta+one_day)
            ]

            date_mask = pd.DatetimeIndex(day_array_movil['Date'])

            # Auxiliar variables
            cnc_day = []
            cnt_day = 0
            trigger_day = False

            for i, date_day in enumerate(dys):
                # Get day and mask
                dy = date_day.day
                mask = np.in1d(date_mask.day.values , dy)

                # Trigger the counting
                if np.count_nonzero(mask) > 0:
                    trigger_day = True

                # Starting the day adquisition
                if trigger_day:

                    cnt_day = cnt_day + 1
                    cnc_day.append(dy)

                    # Averaging val samples
                    if cnt_day == value or i == len(dys)-1:
                        mask = np.in1d(date_mask.day.values , cnc_day)
                        day_sample = day_array_movil[mask]

                        cnt_day = 0
                        cnc_day = []

                        if np.count_nonzero(mask) > 0:
                            mg = day_sample.describe().values.flatten()
                            cols_data = {}
                            cols_data.update({'Date': init_date, 'tau_count':mg[0], 'tau_mean':mg[1],
                                      'tau_std': mg[2], 'tau_25':mg[4], 'tau_50':mg[5], 'tau_75':mg[6], 'tau_max':mg[7],
                                      'tau_min': mg[3]
                                     })
                            rows_data_stat.append(cols_data)
                            if verbose:
                                print (day_sample.describe())

                        else:
                            if verbose:
                                print_msg('Empty span', 'warning')

                        # Re-define the sample size and boundaries
                        day_array_movil = sample[
                            (sample['Date'] >= init_date-one_day ) &
                            (sample['Date'] <= init_date+delta+one_day)
                        ]

                        # Updating the boundaries
                        init_date = init_date + delta

                        date_mask = pd.DatetimeIndex(day_array_movil['Date'])

        # H O U R S
        elif cmd == 'hr':
            # Number of hours to read
            numhours = int(np.ceil((end_date-init_date)/np.timedelta64(1, 'h')))

            # Range of dates with an increasing factor of one day
            hrs = []
            hr_count = init_date.hour
            for i in range(numhours):
                if hr_count > 23:
                    hr_count = 0
                hrs.append(hr_count)
                hr_count += 1
            hrs = np.array(hrs)

            # Initial date mask
            # Step in hours
            delta = pd.to_timedelta(val.zfill(2)+':00:00')
            # Definition of one hour
            one_hour = pd.to_timedelta('01:00:00')

            hour_array_movil = sample[
                (sample['Date'] >= init_date-one_hour ) &
                (sample['Date'] <= init_date+delta+one_hour)
            ]

            date_mask = pd.DatetimeIndex(hour_array_movil['Date'])

            # Auxiliar variables
            cnc_hour = []
            cnt_hour = 0
            trigger_hour = False

            for i, hr in enumerate(hrs):
                # Get hour and mask
                mask = np.in1d(date_mask.hour.values , hr)

                # Trigger the counting
                if np.count_nonzero(mask) > 0:
                    trigger_hour = True

                # Starting the hour adquisition
                if trigger_hour:

                    cnt_hour = cnt_hour + 1
                    cnc_hour.append(hr)

                    # Averaging val samples
                    if cnt_hour == value or i == len(hrs)-1:
                        mask = np.in1d(date_mask.hour.values , cnc_hour)
                        hour_sample = hour_array_movil[mask]

                        cnt_hour = 0
                        cnc_hour = []

                        if np.count_nonzero(mask) > 0:
                            mg = hour_sample.describe().values.flatten()
                            cols_data = {}
                            cols_data.update({'Date': init_date, 'tau_count':mg[0], 'tau_mean':mg[1],
                                      'tau_std': mg[2], 'tau_25':mg[4], 'tau_50':mg[5], 'tau_75':mg[6], 'tau_max':mg[7],
                                      'tau_min': mg[3]
                                     })
                            rows_data_stat.append(cols_data)
                            if verbose:
                                print(hour_sample.describe())

                        else:
                            if verbose:
                                print_msg('Empty span', 'warning')

                        # Re-define the sample size and boundaries
                        hour_array_movil = sample[
                            (sample['Date'] >= init_date-one_hour ) &
                            (sample['Date'] <= init_date+delta+one_hour)
                        ]

                        # Updating the boundaries
                        init_date = init_date + delta

                        date_mask = pd.DatetimeIndex(hour_array_movil['Date'])

        # M I N U T E S
        elif cmd == 'mt':
            # Number of hours to read
            numminutes = int(np.ceil((end_date-init_date)/np.timedelta64(1, 'm')))

            # Range of dates with an increasing factor of one day
            mts = []
            mt_count = init_date.minute
            for i in range(numminutes):
                if mt_count > 59:
                    mt_count = 0
                mts.append(mt_count)
                mt_count += 1
            mts = np.array(mts)

            # Initial date mask
            # Step in hours
            delta = pd.to_timedelta('00:'+val.zfill(2)+':00')
            # Definition of one hour
            one_minute = pd.to_timedelta('00:01:00')

            minute_array_movil = sample[
                (sample['Date'] >= init_date-one_minute ) &
                (sample['Date'] <= init_date+delta+one_minute )
            ]

            date_mask = pd.DatetimeIndex(minute_array_movil['Date'])

            # Auxiliar variables
            cnc_minute = []
            cnt_minute = 0
            trigger_minute = False

            for i, mt in enumerate(mts):
                # Get hour and mask
                mask = np.in1d(date_mask.minute.values , mt)

                # Trigger the counting
                if np.count_nonzero(mask) > 0:
                    trigger_minute = True

                # Starting the hour adquisition
                if trigger_minute:

                    cnt_minute = cnt_minute + 1
                    cnc_minute.append(mt)

                    # Averaging val samples
                    if cnt_minute == value or i == len(mts)-1:
                        mask = np.in1d(date_mask.minute.values , cnc_minute)
                        minute_sample = minute_array_movil[mask]

                        cnt_minute = 0
                        cnc_minute = []

                        if np.count_nonzero(mask) > 0:
                            mg = minute_sample.describe().values.flatten()
                            cols_data = {}
                            cols_data.update({'Date': init_date, 'tau_count':mg[0], 'tau_mean':mg[1],
                                      'tau_std': mg[2], 'tau_25':mg[4], 'tau_50':mg[5], 'tau_75':mg[6], 'tau_max':mg[7],
                                      'tau_min': mg[3]
                                     })
                            rows_data_stat.append(cols_data)
                            if verbose:
                                print(minute_sample.describe())
                        else:
                            if verbose:
                                print_msg('Empty span', 'warning')

                        # Re-define the sample size and boundaries
                        minute_array_movil = sample[
                            (sample['Date'] >= init_date-one_minute ) &
                            (sample['Date'] <= init_date+delta+one_minute )
                        ]

                        # Updating the boundaries
                        init_date = init_date + delta

                        date_mask = pd.DatetimeIndex(minute_array_movil['Date'])

        return pd.DataFrame(rows_data_stat)


    def tau_plotter(self, dataframe, figs, mean=True, boxplot=True, mean_color='r', edge_color='k', med_color='blue', **kwargs):
        """
            Tau plotter tool
            Parameters
            ----------
            dataframe : pandas dataframe
                Dataframe with tau data
            figs : array
                figs[0]: figure
                figs[1]: axes
            mean : boolean
                Show the mean
            boxplot : bool
                Show statistics as boxplot figures
            mean_color : string
                Color to show the mean
            edge_color : string
                Color to show the quartils
            med_color : string
                Color to show the median
            **kwargs : additional keywords (for verbose)           
            ----------
        """
        fig = figs[0]
        axes = figs[1]

        #fig, axes = subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
        fig.subplots_adjust(bottom=0.15, top=0.95, left=0.08, right=0.95)

        row_stats = []
        n_points = len(dataframe.index)

        # Extract the percentils
        q1 = dataframe['tau_25'].values
        med = dataframe['tau_50'].values
        q3 = dataframe['tau_75'].values

        # Extract the limits
        low = dataframe['tau_min'].values
        high = dataframe['tau_max'].values

        # Extract the mean
        avg = dataframe['tau_mean'].values

        # Extract x axis
        n_points = len(dataframe.index)

        # Date limits
        init_date = dataframe['Date'].iloc[0]
        end_date = dataframe['Date'].iloc[n_points-1]

        pos_x = ((dataframe['Date']-init_date)/np.timedelta64(1,'m')).values
        step = np.min(np.diff(pos_x))

        widths = 0.85*step*np.ones_like(pos_x)

        if boxplot:
            for i in range(n_points):
                stats = {}
                stats.update({
                    "med": med[i],      # Median or 50%
                    "q1": q1[i],        # 25%
                    "q3": q3[i],        # 75%
                    "whislo": low[i],   # Minimum
                    "whishi": high[i],  # Maximum
                    "fliers": []
                    })

                row_stats.append(stats)

            box = axes.bxp(row_stats, positions=pos_x, widths=widths)#, patch_artist=True)
            for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
                setp(box[element], color=edge_color)

            for element in ['medians']:
                setp(box[element], color=med_color)

        if mean:
            axes.plot(pos_x, avg, mean_color+'s-')

        if mean or boxplot:
            axes.set_xticklabels( dataframe['Date'], rotation=45 )
            axes.set_xlim(np.min(pos_x) - step, np.max(pos_x) + step)
            axes.set_ylabel(r'Opacity $\tau$',fontsize=20)
            axes.tick_params(axis='y', labelsize=20)

            show()

        return 0


    def tau_plotter_hughes_format(self, dataframe, figs, show_limits=False, **kwargs):
        """
            To plot tau as D. Hughes suggests
            Parameters
            ----------
            dataframe : pandas dataframe
                Dataframe with tau data
            figs : array
                figs[0]: figure
                figs[1]: axes
            show_limits : boolean
                Show the 2mm and 8mm PWV limits
            **kwargs : additional keywords (for verbose)           
            ----------
        """
        fig = figs[0]
        axes = figs[1]

        fig.subplots_adjust(bottom=0.1, top=0.95, left=0.08, right=0.95)

        row_stats = []
        n_points = len(dataframe.index)

        # Extract the percentiles
        q1 = dataframe['tau_25'].values
        med = dataframe['tau_50'].values
        q3 = dataframe['tau_75'].values

        # Extract the mean
        avg = dataframe['tau_mean'].values

        # Extract x axis
        n_points = len(dataframe.index)

        # Date limits
        init_date = dataframe['Date'].iloc[0]
        end_date = dataframe['Date'].iloc[n_points-1]

        pos_x = ((dataframe['Date']-init_date)/np.timedelta64(1,'m')).values

        axes.plot(pos_x, q1, 'bs-', label=r'First Quartile')
        axes.plot(pos_x, med, 'gs--', label=r'Median')
        axes.plot(pos_x, q3, 'rs-.', label=r'Third Quartile')

        # If limits are adjusted
        if show_limits:
            axes.axhline(0.1, color='k', linestyle='--')
            axes.axhline(0.4, color='k', linestyle='--')
            axes.text(pos_x[-1], 0.11, r'2mm PWV')
            axes.text(pos_x[-1], 0.41, r'8mm PWV')

        axes.set_xticks(pos_x)
        #axes.set_xticklabels(dataframe['Date'], rotation=45)
        axes.set_xticklabels(['January','February','March','April','May','June','July','August','September','October', 'November','December'], rotation=0)

        #axes.set_xlim(np.min(pos_x) - step, np.max(pos_x) + step)
        axes.set_ylabel(r'Opacity $\tau$')
        axes.set_xlabel(r'\textbf{Month of year}')
        axes.tick_params(axis='y')

        axes.legend()

        return 0


# period_filtered = tau.filter(tau.raw_data, '-hr 7,8,9,10,11', verbose=True)
# stat = tau.statistics_sample(period_filtered, '-yr 1', verbose=True)
#
# figs = subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
# tau.tau_plotter(stat, figs, med_color="#dd8716", mean=False)
#
# figs[1].set_xticklabels(['June','July','August','September','October', 'November','December',
# 'January', 'February', 'March', 'April', 'May','June','July','August','September','October',
# 'November','December', 'January', 'February', 'March', 'April', 'May','June','July','August',
# 'September','October', 'November','December','January','February', 'March', 'April', 'May','June',
# 'July','August','September','October', 'November','December', 'January', 'February', 'March', 'April',
# 'May','June','July','August','September','October', 'November','December','January', 'February', 'March',
# 'April', 'May','June','July','August','September','October', 'November','December',
# 'January', 'February', 'March', 'April', 'May','June','July','August','September','October',
# 'November','December','January', 'February', 'March'], fontsize=20)
#
# figs[1].set_xticklabels(['January', 'February', 'March', 'April', 'May','June','July','August','September','October', 'November','December'], fontsize=20)
# figs[1].set_title('Mornings [7:00-11:00 hrs] 2013-2020', fontsize=20)
#
#
#
# # Para el promedio de todos los meses de todos los años
# fig, axes = subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
# fig.subplots_adjust(bottom=0.15, top=0.95, left=0.08, right=0.95)
#
# med_color="#dd8716"
# edge_color='k'
#
# stat_month = []
# for i in range(12):
#     period = tau.filter(tau.raw_data, '-mn '+str(i+1)+' -hr 7,8,9,10,11', verbose=True)
#     mg = period.describe().values.flatten()
#     stat_month.append(mg)
#
# row_stats = []
# for i in range(12):
#     stats = {}
#     stats.update({
#         "med": stat_month[i][5],      # Median or 50%
#         "q1": stat_month[i][4],        # 25%
#         "q3": stat_month[i][6],        # 75%
#         "whislo": stat_month[i][3],   # Minimum
#         "whishi": stat_month[i][7],  # Maximum
#         "fliers": []
#         })
#
#     row_stats.append(stats)
#
# box = axes.bxp(row_stats, positions=np.arange(1,13,1))#, patch_artist=True)
# for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
#     setp(box[element], color=edge_color)
#
# for element in ['medians']:
#     setp(box[element], color=med_color)
#
# axes.set_xticklabels(['January', 'February', 'March', 'April', 'May','June','July','August','September','October', 'November','December'] , rotation=45 , fontsize=20)
# axes.set_title('Mornings [7:00-11:00 hrs] 2013-2020', fontsize=20)
# #axes.set_xlim(np.min(pos_x) - step, np.max(pos_x) + step)
# axes.set_ylabel(r'Opacity $\tau$',fontsize=20)
# axes.tick_params(axis='y', labelsize=20)








# Morning
months = np.array([[7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10],
                   [7,8,9,10]])

mask_30min = np.array([[False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False],
                 [False, False]])



# Tau LMT object
#tau = tau_lmt(verbose=True)

# Create the frame to plot
#plts = subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
