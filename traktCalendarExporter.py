#!/usr/bin/python

import ConfigParser, os, json

from pytz import timezone, utc
from uuid import uuid4
from urllib2 import urlopen
from urllib import quote
from icalendar import Calendar, Event
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cfg import createOrGetConfiguration
from utils import Data, padWithZero

today = datetime.now().strftime("%Y%m%d")
cfgFile = os.path.expanduser('~/.traktCalExporter.cfg')
cfg = createOrGetConfiguration(cfgFile)
traktShowsUrl = "http://api.trakt.tv/user/calendar/shows.json/%s/%s/%s/21" % (cfg.TraktApiKey, cfg.TraktUser, today)

class EpisodeEvent(object):
    def __init__(self, show, title, season, number, runtime, airtime):
        self.show, self.title, self.season, self.number, self.runtime, self.airtime = show, title, season, number, runtime, airtime
        self.summary = '''%(show)s S%(season)sE%(number)s "%(title)s"''' % locals()
        self.query = quote("%(show)s S%(season)sE%(number)s" % locals())

    def formatDescription(self, fmt):
        return fmt % self.__dict__

def loadShows():
    socket = urlopen(traktShowsUrl)
    showsCalendar = json.load(socket)
    for dateInfo in showsCalendar:
        y,m,d = [ int(x) for x in dateInfo['date'].split('-') ]
        for data in dateInfo["episodes"]:
            episode = Data(data["episode"])
            show = Data(data["show"])
            number = padWithZero(str(episode.number), 2)
            season = padWithZero(str(episode.season), 2)
            runtime = show.runtime
            title = episode.title
            showName = show.title
            dateString = '%s %s' % (dateInfo['date'], show.air_time.upper())
            airtime =  datetime.strptime(dateString, '%Y-%m-%d %I:%M%p').replace(tzinfo = timezone(cfg.ShowsTimezone)).astimezone(utc)

            yield EpisodeEvent(showName, title, season, number, runtime, airtime)

def openOrCreateCalendar():
    if os.path.exists(cfg.ExportFilePath):
        with open(cfg.ExportFilePath, 'rb') as opened:
            return Calendar.from_ical(opened.read())

    cal = Calendar()
    cal.add('prodid', 'Series calendar')
    cal.add('version', '2.0')
    return cal

def createCalendar():
    cal = openOrCreateCalendar()
    for episodeEvent in loadShows():
        if episodeEvent.summary in [ e['summary'] for e in cal.walk('vevent') ]:
            continue

        event = Event()
        event.add('summary', episodeEvent.summary)
        event.add('dtstart', episodeEvent.airtime)
        event.add('dtend', episodeEvent.airtime + relativedelta( minutes = episodeEvent.runtime ))
        event.add('dtstamp', datetime.utcnow())
        event.add('description', episodeEvent.formatDescription(cfg.EventDescriptionFormat))
        event['uid'] = str(uuid4())

        cal.add_component(event)
    
    with open(cfg.ExportFilePath, 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    createCalendar()

