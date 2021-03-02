# Opacity at LMT (2013-2020) "tau-lmt"

Developed by Marcial Becerril. Data taken from opacity measurements at LMT with the radiometer (225 GHz) from 2013 to 2020.
http://lmtgtm.org/?lang=es

More data related to the instrument: http://wiki.lmtgtm.org/site.html

tau-lmt is a set of tools that easily analize and display the opacities measurements.
It includes:
- Filter opacity data by year, month, day, hour and minute
- Get basic statistic from a period of data (filtered or not): mean, median, quartils.

## Requirements 📋

- Python 3.6 or later
- Pandas >= 1.2.2
- Matplotlib >= 3.3.4

## Install

Clone or download-unzip this GitHub repository. Change the directory to the tau-lmt package.

```python
cd tau_lmt/
```
## Usage example

Import tau-lmt package

```python
from tau_lmt import *
```

Instance the tau object:

```python
tau = tau_lmt()
```

## Filter data

To select (or filter) some periods of time (between 2013-2020):

```python
# tau.raw_data : Data to be filtered. The data.raw_data means the full data 2013-2020, 
#                but it could be any as dataframe format.
# filter_chain : Criteria to filter.

# For example, this line means that we are taking data between the hours 18-20, 
# the months of February, March and April, from the year 2015.
filter_chain = '-yr 2015 -mn 2,3,4 -hr 18,19,20'

filtered_tau = tau.filter(tau.raw_data, filter_chain)
```
## Get statistic

To get the statistic along a defined period of time, as mean, median, standard deviation and quartils; is as follows:

```python
# data        : Data to get statistic.
# stat_chain  : Statistic chain

# Here we are getting the statistic clustering by one month.
stat_chain = '-mn 1'

statistics_tau = tau.statistics_sample(data, stat_chain)
```

## Plot data

To plot opacity data, tau-lmt uses to models:
-"tau_plotter". Plot mean, median and quartils as boxplots.
-"tau_plotter_hughes_format". Plot opacity following the format used here: http://wiki.lmtgtm.org/site.html

### tau_plotter

```python
# Create the canvas
figs = subplots(nrows=1, ncols=1)
# Plot data
tau.tau_plotter(statistics_tau, figs)
```

### tau.tau_plotter_hughes_format

```python
# Create the canvas
figs = subplots(nrows=1, ncols=1)
# Plot data
 tau.tau_plotter_hughes_format(statistics_tau, figs)
```

To know th rest of the plotting parameters use:

```python
tau.tau_plotter?
tau.tau_plotter_hughes_format?
```
