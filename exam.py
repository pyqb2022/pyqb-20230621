# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Programming in Python
# ## Exam: June 21, 2023
#
# You can solve the exercises below by using standard Python 3.10 libraries, NumPy, Matplotlib, Pandas, PyMC.
# You can browse the documentation: [Python](https://docs.python.org/3.10/), [NumPy](https://numpy.org/doc/stable/user/index.html), [Matplotlib](https://matplotlib.org/stable/users/index.html), [Pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html), [PyMC](https://docs.pymc.io).
# You can also look at the [slides of the course](https://homes.di.unimi.it/monga/lucidi2223/pyqb00.pdf) or your code on [GitHub](https://github.com).
#
# **It is forbidden to communicate with others.**
#
# To test examples in docstrings use
#
# ```python
# import doctest
# doctest.testmod()
# ```
#

import numpy as np
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pymc as pm   # type: ignore
import arviz as az   # type: ignore

# ### Exercise 1 (max 4 points)
#
# The file [rhinos.csv](./rhinos.csv) (Duthé, Vanessa (2023), Reductions in home-range size and social interactions among dehorned black rhinoceroses (Diceros bicornis), Dryad, Dataset, https://doi.org/10.5061/dryad.gf1vhhmt5) contains:
#
# - Date: date of rhino sighting
# - RhinosAtSighting: id of individual rhino
# - Sex: sex of individual rhino
# - Horn: indicating horned or dehorned rhino at time of sighting
# - DateBorn: date of birth of individual rhino
# - Reserve: reserve where sighting occured
#
# Read the data in a pandas DataFrame. Be sure  that the columns `Date` and `DateBorn` has dtype `pd.datetime64[ns]`.
#

data = pd.read_csv('rhinos.csv', sep=';', parse_dates=['Date', 'DateBorn'], dayfirst=True)
data.dtypes

# ### Exercise 2 (max 4 points)
#
# Add a column `Age` with the age in years of the rhinos at the time of the sighting.
#

data['Age'] = (data['Date'] - data['DateBorn']).astype(int) / (365*24*60*60*10**9)

# ### Exercise 3 (max 7 points)
#
# Define a function `dehorn_trend` that takes a list of pairs (a, b), where a is a date (a `pd.datetime64[ns]`) and b is a boolean value, denoting if a rhino was dehorned (`True`) or horned (`False`); the function returns the list of the pairs in which the horned/dehorned state changed. For example, if the input list is `[(pd.to_datetime('1.1.1989'), True), (pd.to_datetime('1.1.1990'), False), (pd.to_datetime('1.1.1995'), False)]`, the function should return `[(pd.to_datetime('1.1.1989'), True), (pd.to_datetime('1.1.1995'), False)]`; in other words, when in a sequence of pairs the right side has the same value, you should keep only the last pair. You can assume the pairs are ordered by increasing date.
#
# To get the full marks, you should declare correctly the type hints and add a test within a doctest string.

# +
import datetime

def dehorn_trend(lst: list[tuple[datetime.datetime, bool]]) -> list[tuple[datetime.datetime, bool]]:
    """Return the list of the pairs in which the horned/dehorned state changed. 
    
    >>> dehorn_trend([(pd.to_datetime('1.1.1989'), True), 
    ...               (pd.to_datetime('1.1.1990'), False), 
    ...               (pd.to_datetime('1.1.1995'), False)])
    [(Timestamp('1989-01-01 00:00:00'), True), (Timestamp('1995-01-01 00:00:00'), False)]
    """
    ris = lst[0:1]
    state = lst[0][1]
    for i in range(1, len(lst)):
        if lst[i][1] == state:
            ris[-1] = lst[i]
        else:
            ris.append(lst[i])
            state = lst[i][1]
    
    return ris


# -

import doctest
doctest.testmod()

# ### Exercise 4 (max 4 points)
#
# Apply the function defined in Exercise 3 to the data referring to rhino MPGRBF-02-05.

# +
data['dehorned'] = data['Horn'] == 'Dehorned'

arg = [tuple(x) for _, x in 
       data[data['RhinosAtSighting'] == 'MPGRBF-02-05'][['Date', 'dehorned']].sort_values(by='Date').iterrows()]


dehorn_trend(arg)
# -

# ### Exercise 5 (max 2 points)
#
# Compute the ratio dehorned/(all individual sightings) for each rhino

data.groupby('RhinosAtSighting')['dehorned'].mean()

# ### Exercise 6 (max 3 points)
#
# Plot a histogram of the number of rhinos observed in each reserve

# +
nums = data.groupby('Reserve')['RhinosAtSighting'].count()

fig, ax = plt.subplots(1)
ax.bar(nums.index, nums, label='Number of rhinos')
ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha='right')
_ = ax.legend()
# -

# ### Exercise 7 (max 3 points)
#
# Plot together the histograms of the number of male and female rhinos observed in each reserve

# +
nums_f = data[data['Sex'] == 'Female'].groupby('Reserve')['RhinosAtSighting'].count()
nums_m = data[data['Sex'] == 'Male'].groupby('Reserve')['RhinosAtSighting'].count()


fig, ax = plt.subplots(1)
ax.bar(range(len(nums_f)), nums_f, width=-.4, align='edge', label='Number of female rhinos')
ax.bar(range(len(nums_m)), nums_m, width=.4, align='edge', label='Number of male rhinos')

ax.set_xticks(range(len(nums)), nums.index, rotation=45, ha='right')
_ = ax.legend()
# -

# ### Exercise 8 (max 6 points)
#
# Consider this statistical model:
#
# - a parameter $\alpha$ is uniformly distributed between 1 and 50
# - $\sigma$ is exponentially distributed with $\lambda = 1$
# - the observed `age` is normally distributed with a standard deviation of $\sigma$ and a mean given by $\alpha$.
#
# Code this model with pymc, sample the model, and plot the summary of the resulting estimation by using `az.plot_posterior`.
#
#
#
#

with pm.Model() as m:
    a = pm.Uniform('alpha', 1, 50)
    s = pm.Exponential('lambda', 1)
    age = pm.Normal('age', a, s, observed=data['Age'])
    
    idata = pm.sample()
    

_ = az.plot_posterior(idata)


