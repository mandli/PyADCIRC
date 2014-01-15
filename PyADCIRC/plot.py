r"""Plotting functions for ADCIRC data"""

import urllib2

def add_title(axes, time, title="Surface", land_fall = 0.0):
    t = (time - land_fall) / (60**2 * 24) 
    days = int(t)
    hours = (t - int(t)) * 24.0
    axes.set_title('%s at day %3i, hour %2.1f' % (title, days, hours))


def get_google_map_tile():

    urllib2.open()

    return None