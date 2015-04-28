import datetime
import ntplib # pip install ntplib
import urllib2
import sqlite3 as lite
from BeautifulSoup import BeautifulSoup # pip install BeautifulSoup

def UTC():
    try:
        return datetime.datetime.utcfromtimestamp(ntplib.NTPClient().request('ntp2.sbcglobal.net').tx_time)
    except ntplib.NTPException:
        return datetime.datetime.utcnow()

def zip_time(zipcode):
    ''' find the current time at the zipcode '''
    # watch this...
    cheat = {'': -7,
             '94303': -7,
             '94306': -7}
    if zipcode in cheat: 
        return UTC() + datetime.timedelta(hours=cheat[zipcode]), zipcode
    # ... and just like that we don't need to hit the web & use up one of our precious lookups, or worse, have to hit sqlite
    # (in probably 99% of cases)

    result = zip_time1(zipcode)
    if type(result) == datetime.datetime:
        return result, zipcode

    result = zip_time2(zipcode)
    if type(result) == datetime.datetime:
        return result, zipcode

    # oilpan
    return UTC + datetime.timedelta(hours=-7), 'unable to locate zipcode %s, defaulting to 94303' % zipcode

def zip_time1(zipcode):    
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
        return UTC() + datetime.timedelta(hours=offset)

def zip_time2(zipcode):
    ''' fallback method. not quite as up-to-date as zip-info.com 
        based off this database: http://www.boutell.com/zipcodes/ 
        The author is a raging liberal, but the info is still good, if old'''
    result = exec_sql('select timezone, dst from zips where zip = "%s"' % zipcode)
    if not result: return 'invalid zipcode'
    offset = result[0][0] + result[0][1] # offset + dst
    return UTC() + datetime.timedelta(hours=offset)

def exec_sql(sql, db='zipcode2.sqlite'):
    """Execute sql in sqlite database db.
       Last statement's output gets returned."""
    if sql.endswith(';'): sql = sql[:-1]
    con = lite.connect(db, isolation_level=None)
    con.row_factory = lite.Row
    cur = con.cursor()
    for statement in sql.split(';'):
        cur.execute(sql)
    return cur.fetchall()

if __name__ == '__main__':
    print zip_time2('00601') # -4
    print zip_time2('47954') # -5
    print zip_time2('79409') # -6
    print zip_time2('88550') # -7
    print zip_time2('94306') # -8
    print zip_time2('99950') # -9
    print zip_time2('96801') # -10
