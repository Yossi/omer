import datetime
import ntplib # pip install ntplib
import urllib2
from BeautifulSoup import BeautifulSoup # pip install BeautifulSoup
from secrets import dbhost, db, dbuser, dbpasswd
import pymysql # pip install pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import logging

import warnings
warnings.filterwarnings('error', category=MySQLdb.Warning)

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
            self.connection = MySQLdb.connect(**self.credentials)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

cm = CM()
cm.set_credentials({'host': dbhost, 'db': db, 'user': dbuser, 'passwd': dbpasswd})

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

    except MySQLdb.OperationalError as exc:
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
    try:
        return datetime.datetime.utcfromtimestamp(ntplib.NTPClient().request('ntp2.sbcglobal.net').tx_time)
    except ntplib.NTPException:
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
    result = exec_sql('SELECT timezone, dst FROM zips WHERE zip = "%s"' % zipcode)
    if not result: return 'zipcode not found'
    offset = result[0][0] + result[0][1] # offset + dst
    return UTC() + datetime.timedelta(hours=offset)

def zip_time_web(zipcode):
    url = 'http://www.zip-info.com/cgi-local/zipsrch.exe?tz=tz&zip='
    soup = BeautifulSoup(urllib2.urlopen(url+zipcode).read())
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
        exec_sql('INSERT INTO zips VALUES ("%s", %s, %s)' % (zipcode, offsets[result['timezone']], int(daylight))) # stash result for next time
        return UTC() + datetime.timedelta(hours=offset)

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
'''

# secondary db of zips available here
# http://www.boutell.com/zipcodes/