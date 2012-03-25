#!/usr/bin/python

import ConfigParser, os, json

from pytz import timezone
from uuid import uuid4
from urllib2 import urlopen
from urllib import quote
from icalendar import Calendar, Event
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cfg import createOrGetConfiguration
from utils import Data, padWithZero

cfgFile = os.path.expanduser('~/.traktCalExporter.cfg')
cfg = createOrGetConfiguration(cfgFile)
traktShowsUrl = "http://api.trakt.tv/user/calendar/shows.json/%s/%s" % (cfg.TraktApiKey, cfg.TraktUser)

class EpisodeEvent(object):
    def __init__(self, show, title, season, number, runtime, airtime):
        self.show, self.title, self.season, self.number, self.runtime, self.airtime = show, title, season, number, runtime, airtime

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
            airtime =  datetime.strptime(dateString, '%Y-%m-%d %I:%M%p').replace(tzinfo = timezone(cfg.ShowsTimezone)).astimezone(timezone(cfg.UserTimezone))

            yield EpisodeEvent(showName, title, season, number, runtime, airtime)

def createCalendar():
    cal = Calendar()
    cal.add('prodid', 'Series calendar')
    cal.add('version', '2.0')

    for episodeEvent in loadShows():
        event = Event()
        show, season, number, title = episodeEvent.show, episodeEvent.season, episodeEvent.number, episodeEvent.title
        summary = '''%(show)s S%(season)sE%(number)s "%(title)s"''' % locals()
        query = quote(summary)
        description = cfg.EventDescriptionFormat % locals()

        event.add('summary', summary)
        event.add('dtstart', episodeEvent.airtime)
        event.add('dtend', episodeEvent.airtime + relativedelta( minutes = episodeEvent.runtime ))
        event.add('dtstamp', datetime.now().replace(tzinfo = timezone(cfg.UserTimezone)))
        event.add('description', description)
        event['uid'] = str(uuid4())

        cal.add_component(event)
    
    with open(cfg.ExportFilePath, 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    createCalendar()

