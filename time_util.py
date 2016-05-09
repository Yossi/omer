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
    return UTC + datetime.timedelta(hours=-7), 'unable to locate zipcode %s, defaulting to 94303' % zipcode

def zip_time_db(zipcode):
    result = exec_sql('select timezone, dst from zips where zip = "%s"' % zipcode)
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
        exec_sql('insert into zips values (%s, %s, %s)' % (zipcode, offsets[result['timezone']], int(daylight))) # stash result for next time
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
    assert zip_time('00601') == -4
    assert zip_time('47954') == -5
    assert zip_time('79409') == -6
    assert zip_time('88550') == -7
    assert zip_time('94306') == -8
    assert zip_time('99950') == -9
    assert zip_time('96801') == -10

# code to create SQLite table
#exec_sql('create table zips (zip text primary key not null, timezone int, dst int)')
# secondary db of zips available here
# http://www.boutell.com/zipcodes/