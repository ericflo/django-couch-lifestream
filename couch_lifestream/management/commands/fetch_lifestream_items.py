import datetime
import time
from django.core.management.base import NoArgsCommand
from django.conf import settings
from urllib2 import urlopen
from couch_lifestream import db

try:
    import simplejson as json
except ImportError:
    import json

TWITTER_USERNAME = getattr(settings, 'TWITTER_USERNAME', None)

def fetch_twitter_items():
    from dateutil.parser import parse
    print "Fetching Twitter items"
    fetched = urlopen('http://twitter.com/statuses/user_timeline.json?id=%s' % (
        TWITTER_USERNAME,)).read()
    data = json.loads(fetched)
    map_fun = 'function(doc) { emit(doc.id, null); }'
    for item in data:
        item['item_type'] = 'twitter'
        item['couch_lifestream_date'] = parse(item['created_at']).isoformat()
        if len(db.query(map_fun, key=item['id'])) == 0:
            db.create(item)
    print "Twitter items fetched"

POWNCE_USERNAME = getattr(settings, 'POWNCE_USERNAME', None)

def fetch_pownce_items():
    print "Fetching Pownce items"
    fetched = urlopen('http://api.pownce.com/2.0/note_lists/%s.json' % (
        TWITTER_USERNAME,)).read()
    data = json.loads(fetched)['notes']
    map_fun = 'function(doc) { emit(doc.id, null); }'
    for item in data:
        item['item_type'] = 'pownce'
        y, month, d, h, m, s, wd, jd, ds = time.gmtime(item['timestamp'])
        couch_lifestream_date = datetime.datetime(y, month, d, h, m, s)
        item['couch_lifestream_date'] = couch_lifestream_date.isoformat()
        if len(db.query(map_fun, key=item['id'])) == 0:
            db.create(item)
    print "Pownce items fetched"

REDDIT_USERNAME = getattr(settings, 'REDDIT_USERNAME', None)

def fetch_reddit_items():
    import feedparser
    print "Fetching Reddit items"
    d = feedparser.parse('http://www.reddit.com/user/%s/comments/.rss' % (
        REDDIT_USERNAME,))
    map_fun = 'function(doc) { emit(doc.link, null); }'
    for item in map(dict, d['entries']):
        item['item_type'] = 'reddit-comment'
        item['couch_lifestream_date'] = datetime.datetime.fromtimestamp(
            time.mktime(item['updated_parsed']))
        if len(db.query(map_fun, key=item['link'])) == 0:
            for (key, val) in item.items():
                if 'parsed' in key:
                    del item[key]
                elif isinstance(val, datetime.datetime):
                    item[key] = val.isoformat()
                elif isinstance(val, datetime.date):
                    item[key] = val.isoformat()
            db.create(item)
    print "Reddit items fetched"

FLICKR_USER_ID = getattr(settings, 'FLICKR_USER_ID', None)

def fetch_flickr_items():
    import feedparser
    print "Fetching Flickr items"
    d = feedparser.parse('http://api.flickr.com/services/feeds/photos_public.gne?format=atom&id=%s' % (FLICKR_USER_ID,))
    map_fun = 'function(doc) { emit(doc.id, null); }'
    for item in map(dict, d['entries']):
        item['item_type'] = 'flickr'
        item['couch_lifestream_date'] = datetime.datetime.fromtimestamp(
            time.mktime(item['updated_parsed']))
        if len(db.query(map_fun, key=item['id'])) == 0:
            for (key, val) in item.items():
                if 'parsed' in key:
                    del item[key]
                elif isinstance(val, datetime.datetime):
                    item[key] = val.isoformat()
                elif isinstance(val, datetime.date):
                    item[key] = val.isoformat()
            db.create(item)
    print "Flickr items fetched"

class Command(NoArgsCommand):
    help = 'Fetch the latest lifestream items and insert them into CouchDB.'
    
    def handle_noargs(self, **options):
        if TWITTER_USERNAME is not None:
            fetch_twitter_items()
        if POWNCE_USERNAME is not None:
            fetch_pownce_items()
        if REDDIT_USERNAME is not None:
            fetch_reddit_items()
        if FLICKR_USER_ID is not None:
            fetch_flickr_items()
        print "Finished loading lifestream items."