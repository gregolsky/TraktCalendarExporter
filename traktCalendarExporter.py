#!/usr/bin/python
import pytz
import subprocess
import json

from uuid import uuid4
from urllib2 import urlopen
from icalendar import Calendar, Event
from datetime import datetime
from dateutil.relativedelta import relativedelta

usTimezone = pytz.timezone('US/Central')
usNow = usTimezone.localize(datetime.now())
calFile = '/tmp/series.ics'

TRAKT_API_KEY = ""
TRAKT_USER = ""

traktShowsUrl = "http://api.trakt.tv/user/calendar/shows.json/%s/%s" % (traktApiKey, traktUser)

class Data:
    def __init__(self, data):
        self.__dict__.update(data)

    def __repr__(self):
        return str(self.__dict__)

def padWithZero(s, length):
    result = s    
    while len(result) < length:
        result = "0%s" % result
    return result

def loadShows():
    socket = urlopen(traktShowsUrl)
    showsCalendar = json.load(socket)
    for dateInfo in showsCalendar:
        y,m,d = [ int(x) for x in dateInfo['date'].split('-') ]
        episodeData = {}
        for data in dateInfo["episodes"]:
            episode = Data(data["episode"])
            show = Data(data["show"])
            episodeData["number"] = episode.number
            episodeData['season'] = episode.season
            episodeData['runtime'] = show.runtime
            episodeData['title'] = episode.title
            episodeData['show'] = show.title
            dateString = '%s %s' % (dateInfo['date'], show.air_time.upper())
            episodeData['airTime'] =  datetime.strptime(dateString, '%Y-%m-%d %H:%M%p')
            yield Data(episodeData)

def createCalendar():
    cal = Calendar()
    cal.add('prodid', 'Series calendar')
    cal.add('version', '2.0')

    for episodeEvent in loadShows():
        event = Event()
        name, season, episodeNr, title = episodeEvent.show, episodeEvent.season, episodeEvent.number, episodeEvent.title
        nameUrlEncoded = episodeEvent.show.replace(' ', '+')
        summary = '%(name)s S%(season)sE%(episodeNr)s %(title)s' % locals()
        description = ""
        
        event.add('summary', summary)
        event.add('dtstart', episodeEvent.airTime)
        event.add('dtend', episodeEvent.airTime + relativedelta( minutes = episodeEvent.runtime ))
        event.add('dtstamp', datetime.now())
        event.add('description', description)
        event['uid'] = str(uuid4())

        cal.add_component(event)
    
    with open(calFile, 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    createCalendar()

