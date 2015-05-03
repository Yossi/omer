#!/usr/bin/python

# this project depends on the following being available, you can get them via pip
# pip install python-dateutil feedparser ntplib BeautifulSoup

import sys, os
sys.path.append(os.path.dirname(__file__))

from dateutil.parser import parse # pip install python-dateutil
import feedparser # pip install feedparser

from hebrew import textforday
import time_util # pip install ntplib BeautifulSoup
reload(time_util) # I think what happens is sometimes time_util sometimes gets cached and gets stuck returning the same time forever. This fixes that.

from flask import Flask # pip install flask
from flask import request
app = Flask(__name__)

def omer_day(heb_date):
    ''' returns the day of the omer for the given hebrew date (i.e. answers the question "what omer do we count on the evening it becomes this date?")
        returns None if the date is not during the omer
    '''
    month, day = heb_date.partition(',')[0].rpartition(' ')[::2]

    #if nissan and day > 16: omer = day - 15
    #if iyar: omer = 15 + day
    #if sivan and day < 5: omer = 44 + day

    offset = {'Nissan': -15,
              'Iyar': 15,
              'Sivan': 44}

    omer = int(day) + offset.get(month, 50) # 50 to make sure it is always out of range the rest of the year
    return omer if omer in range(1,50) else None

def chabad_org(zipcode):
    ''' returns a tuple of the hebrew date for the majority of today's gregorian date (as the server sees it) and 
        the times of dawn, sunset, and nightfall for the given zipcode '''
    times = {'now': time_util.zip_time(zipcode),
             'zipcode': zipcode}

    feed = 'http://www.chabad.org/tools/rss/zmanim.xml?z=%s&tDate=%s' % (zipcode, times['now'][0].strftime('%m/%d/%Y'))
    info = feedparser.parse(feed)
    for entry in info.entries:
        if 'dawn' in entry.title:
            times['dawn'] = parse(entry.title.split('-')[1])
        if 'sunset' in entry.title:
            times['sunset'] = parse(entry.title.split('-')[1])
        if 'nightfall' in entry.title:
            times['nightfall'] = parse(entry.title.split('-')[1])
    return info.feed.hebrew_date, times

times = {}
def refine_day(zipcode='94303'):
    ''' adjusts for before/after tzeit '''
    global times
    heb_date, times = chabad_org(zipcode)
    day = omer_day(heb_date)
    if day:
        return int(day) + int(times['now'][0] > times['sunset']) # boolean turned into an int
    return -1

def date_line(dateline):
    results = {'east': 1, 'west': -1, '1': 1, '-1': -1}
    return results.get(dateline.lower(), 0)

@app.route('/')
def omer():
    form = request.args
    zipcode = form.get('zipcode') or '94303'
    day = form.get('day') or refine_day(zipcode)
    dateline = form.get('dateline', '')
    try: day = int(day) + date_line(dateline)
    except ValueError: pass

    return textforday(day, times).encode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
