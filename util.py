from datetime import datetime

import feedparser
from dateutil.parser import parse
from dateutil.tz import gettz
from timezonefinder import TimezoneFinder
from uszipcode import SearchEngine
from pyluach import dates, hebrewcal

def ll_to_zip(latitude, longitude):
    search = SearchEngine(simple_zipcode=True)
    return search.by_coordinates(float(latitude), float(longitude), radius=50, returns=1)[0].zipcode

def zip_to_ll(zipcode):
    search = SearchEngine(simple_zipcode=True)
    result = search.by_zipcode(zipcode)
    return result.lat, result.lng

def ll_to_tz(latitude, longitude):
    tf = TimezoneFinder()
    return tf.timezone_at(lat=latitude, lng=longitude)

def time_at_zip(zipcode):
    timezone = gettz(ll_to_tz(*zip_to_ll(zipcode)))
    now = datetime.now(timezone)
    return now

def date_line_offset(dateline):
    results = {'east': 1, 'west': -1, '1': 1, '-1': -1}
    return results.get(dateline.lower(), 0)

def hebrew_date(greg_date):
    heb = dates.HebrewDate.from_pydate(greg_date)
    return f'{hebrewcal.Month(heb.year, heb.month).name} {heb.day}, {heb.year}'

def chabad_org(zipcode, date=''):
    ''' returns a tuple of the hebrew date for the majority of today's gregorian date (as the server sees it) and
        the times of dawn, sunset, and nightfall for the given zipcode '''
    times = {'now': time_at_zip(zipcode)} # current time at zipcode

    if not date:
        date = times['now']

    feed = f"http://www.chabad.org/tools/rss/zmanim.xml?z={zipcode}&tDate={date.strftime('%m/%d/%Y')}"
    info = feedparser.parse(feed)
    if not info.get('bozo') and False:
        for entry in info.entries:
            if 'dawn' in entry.title.lower():
                times['dawn'] = parse(entry.title.split('-')[1], default=date).replace(tzinfo=gettz(ll_to_tz(*zip_to_ll(zipcode))))
            if 'sunset' in entry.title.lower():
                times['sunset'] = parse(entry.title.split('-')[1], default=date).replace(tzinfo=gettz(ll_to_tz(*zip_to_ll(zipcode))))
            if ('nightfall' in entry.title.lower() or
                'candle lighting after' in entry.title.lower() or
                'holiday ends' in entry.title.lower() or
                'shabbat ends' in entry.title.lower()):
                times['nightfall'] = parse(entry.title.split('-')[1], default=date).replace(tzinfo=gettz(ll_to_tz(*zip_to_ll(zipcode))))
    return hebrew_date(date), times

def omer_day(heb_date):
    ''' returns the day of the omer for the given hebrew date (i.e. answers the question "what omer do we count on the evening it becomes this hebrew date?")
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
    return omer if omer in range(1, 50) else None

def process_args(args):
    if all(args['ll']):
        args['zipcode'] = ll_to_zip(*args['ll'])

    try:
        args['date'] = parse(args['date'], fuzzy=True)
    except:
        args['date'] = ''
    args['print'] = bool(args['date'])

    heb_date, times = chabad_org(args['zipcode'], args['date'])
    args.update(times)

    if not args['passed_day']:
        day_of_omer = omer_day(heb_date)

        try: day_of_omer = int(day_of_omer) + date_line_offset(args['dateline'])
        except TypeError: pass

        if day_of_omer:
            if not args['print']:
                day_of_omer = int(day_of_omer) + int(args['now'] > args.get('sunset', args['now'].replace(hour=12, minute=00, second=00))) # boolean cast to an int
            else:
                day_of_omer = int(day_of_omer) + 1
        else:
            day_of_omer = -1
    else:
        day_of_omer = int(args['passed_day'])

    args['day_of_omer'] = day_of_omer


if __name__ == '__main__':
    from pprint import pprint
    args = {
        'zipcode': '94303',
        'date': '',
        'dateline': '',
        'll': (None, None),
        'passed_day': None
    }
    process_args(args)
    pprint(args)
