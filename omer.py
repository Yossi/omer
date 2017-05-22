#!/usr/bin/python

# this project depends on the following being available, you can get them via pip
# pip install python-dateutil feedparser ntplib BeautifulSoup

import sys, os
import logging
logging.basicConfig(stream=sys.stderr)

from dateutil.parser import parse # pip install python-dateutil
import feedparser # pip install feedparser

from hebrew import textforday
import time_util # pip install ntplib BeautifulSoup
from imp import reload
reload(time_util) # I think what happens is sometimes time_util gets cached and ends up returning the same time forever. This fixes that.

from flask import Flask, request, send_from_directory # pip install flask
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

def chabad_org(zipcode, date=''):
    ''' returns a tuple of the hebrew date for the majority of today's gregorian date (as the server sees it) and 
        the times of dawn, sunset, and nightfall for the given zipcode '''
    times = {'now': time_util.zip_time(zipcode),
             'zipcode': zipcode,
             'print' : bool(date)}

    if not date:
        date = times['now'][0].strftime('%m/%d/%Y')

    feed = 'http://www.chabad.org/tools/rss/zmanim.xml?z=%s&tDate=%s' % (zipcode, date)
    info = feedparser.parse(feed)
    for entry in info.entries:
        if 'dawn' in entry.title.lower():
            times['dawn'] = parse(date + entry.title.split('-')[1])
        if 'sunset' in entry.title.lower():
            times['sunset'] = parse(date + entry.title.split('-')[1])
        if ('nightfall' in entry.title.lower() or 
            'candle lighting after' in entry.title.lower() or
            'holiday ends' in entry.title.lower() or
            'shabbat ends' in entry.title.lower()):
            times['nightfall'] = parse(date + entry.title.split('-')[1])
    return info.feed.hebrew_date, times

times = {}
def refine_day(zipcode='94303', date=''):
    ''' adjusts for before/after tzeit '''
    global times
    heb_date, times = chabad_org(zipcode, date)
    day = omer_day(heb_date)
    if day:
        if not times['print']:
            return int(day) + int(times['now'][0] > times['sunset']) # boolean turned into an int
        else:
            return int(day) + 1
    return -1

def date_line(dateline):
    results = {'east': 1, 'west': -1, '1': 1, '-1': -1}
    return results.get(dateline.lower(), 0)

@app.route('/')
def omer():
    form = request.args
    zipcode = form.get('zipcode') or '94303'
    date = form.get('date') or ''
    day = refine_day(zipcode, date)
    day = form.get('day') or day 
    dateline = form.get('dateline', '')
    try: day = int(day) + date_line(dateline)
    except ValueError: pass

    return textforday(day, times).encode('utf-8')

@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory('data/fonts', path)

if __name__ == '__main__':
    app.run(debug=True)
