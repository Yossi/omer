import datetime
import requests # pip install requests
from bs4 import BeautifulSoup # pip install BeautifulSoup4
from secrets import dbconfig
import pymysql # pip install pymysql
import logging

import warnings
warnings.filterwarnings('error', category=pymysql.Warning)

class CM(object):
    ''' connection manager '''
    def __init__(self):
        self.connection = None

    def set_credentials(self, credentials):
        self.credentials = credentials
        self.close()

    def get_conn(self):
        if not self.connection:
            logging.info('no db connection. creating...')
            self.connection = pymysql.connect(**self.credentials)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

cm = CM()
cm.set_credentials(dbconfig)

def exec_sql(sql, retries=2):
    try:
        cur = None # needed in case get_conn() dies
        db = cm.get_conn()
        cur = db.cursor()
        cur.execute(sql)
        rows = [r for r in cur.fetchall()]
        if not rows and not sql.strip().lower().startswith('select'):
            rows = cur.rowcount
        cur.close()
        db.commit()
        return rows

    except pymysql.OperationalError as exc:
        if cur:
            cur.close()
        cm.close()
        if retries:
            logging.warning('sql query failed, retrying')
            return exec_sql(sql, retries-1)
        else:
            raise

    except:
        logging.error(sql)
        raise

def UTC():
    return datetime.datetime.utcnow()

def zip_time(zipcode):
    ''' find the current time at the zipcode '''
    cheat = {'': -7,
             '94303': -7}
    if zipcode in cheat:
        return UTC() + datetime.timedelta(hours=cheat[zipcode]), zipcode

    result = zip_time_db(zipcode)
    if type(result) == datetime.datetime:
        return result, zipcode

    result = zip_time_web(zipcode)
    if type(result) == datetime.datetime:
        return result, zipcode

    # oilpan
    return UTC() + datetime.timedelta(hours=-7), 'unable to locate zipcode %s, defaulting to 94303' % zipcode

def zip_time_db(zipcode):
    result = exec_sql('SELECT timezone, dst FROM zips WHERE zip = "%s";' % zipcode)
    if not result: return 'zipcode not found'
    offset = result[0][0] + result[0][1] # offset + dst
    return UTC() + datetime.timedelta(hours=offset)

def zip_time_web(zipcode):
    url = 'http://www.zip-info.com/cgi-local/zipsrch.exe?tz=tz&zip='
    soup = BeautifulSoup(requests.get(url+zipcode).text, 'html5lib')
    if not soup('table'): # zipcode lookup limit exeeded. 30 lookups/day/ip
        return 'zipcode lookup limit exeeded'
    result = [td.contents[0] for td in soup('table')[3].findAll('tr')[1]][2:]
    if result[0] != zipcode:
        return 'invalid zipcode'
    else:
        result = dict(zip(['zipcode', 'timezone', 'dst'], result))
        offsets = { 'EST+1': -4,
                    'EST': -5,
                    'CST': -6,
                    'MST': -7,
                    'PST': -8,
                    'PST-1': -9,
                    'PST-2': -10 }
        daylight = result['dst'].startswith('Y')
        offset = offsets[result['timezone']] + daylight # sfira is always in DST if DST is observed
        exec_sql('INSERT INTO zips VALUES ("%s", %s, %s);' % (zipcode, offsets[result['timezone']], int(daylight))) # stash result for next time
        return UTC() + datetime.timedelta(hours=offset)

def lat_lon_to_zip(lat, lon):
    if not (lat and lon): return

    lat = lat[:lat.index('.')+4] # trim to just 3 digits past the decimal
    lon = lon[:lon.index('.')+4] # good enough for zipcodes

    zipcode = lat_lon_to_zip_db(lat, lon)
    if zipcode: return zipcode

    return lat_lon_to_zip_web(lat, lon)

def lat_lon_to_zip_db(lat, lon):
    result = exec_sql('SELECT zip FROM latlons WHERE latlon = "{},{}";'.format(lat, lon))
    if result: return result[0][0]

def lat_lon_to_zip_web(lat, lon):
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="omer reverse geocoder v1")
        location = geolocator.reverse(f'{lat}, {lon}')
        result = {key: location.raw['address'][key] for key in ('postcode', 'country_code')}
        if result['country_code'] != 'us':
            return # not a US lat/lon
        zipcode = result['postcode']
        exec_sql('INSERT INTO latlons VALUES ("{},{}", {});'.format(lat, lon, zipcode))
        return zipcode
    except KeyError:
         return # unable to geocode

if __name__ == '__main__':
    assert zip_time('00601')[0].hour == (UTC() + datetime.timedelta(hours=-4)).hour
    assert zip_time('47954')[0].hour == (UTC() + datetime.timedelta(hours=-5)).hour + 1
    assert zip_time('79409')[0].hour == (UTC() + datetime.timedelta(hours=-6)).hour + 1
    assert zip_time('88550')[0].hour == (UTC() + datetime.timedelta(hours=-7)).hour + 1
    assert zip_time('94306')[0].hour == (UTC() + datetime.timedelta(hours=-8)).hour + 1
    assert zip_time('99950')[0].hour == (UTC() + datetime.timedelta(hours=-9)).hour + 1
    assert zip_time('96801')[0].hour == (UTC() + datetime.timedelta(hours=-10)).hour

# code to create SQL table
'''
CREATE TABLE `zips` (
  `zip` varchar(5) NOT NULL,
  `timezone` int(11) DEFAULT NULL,
  `dst` int(11) DEFAULT NULL,
  PRIMARY KEY (`zip`),
  UNIQUE KEY `zip_UNIQUE` (`zip`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `latlons` (
  `latlon` varchar(15) NOT NULL,
  `zip` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`latlon`),
  UNIQUE KEY `latlon_UNIQUE` (`latlon`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
'''

# secondary db of zips available here
# http://www.boutell.com/zipcodes/
