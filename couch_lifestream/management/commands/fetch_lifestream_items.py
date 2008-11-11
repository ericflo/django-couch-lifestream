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

### HELPER FUNCTIONS ###

def parse_json(url, item_type, callback, discriminator='id', list_key=None):
    print "Fetching %s items" % (item_type,)
    fetched = urlopen(url).read()
    data = json.loads(fetched)
    if list_key:
        data = data[list_key]
    map_fun = 'function(doc) { emit(doc.%s, null); }' % (discriminator,)
    for item in map(callback, data):
        item['item_type'] = item_type
        if len(db.query(map_fun, key=item[discriminator])) == 0:
            db.create(item)
    print "%s items fetched" % (item_type,)

def parse_feed(url, item_type, discriminator='id'):
    import feedparser
    print "Fetching %s items" % (item_type,)
    d = feedparser.parse(url)
    map_fun = 'function(doc) { emit(doc.%s, null); }' % (discriminator,)
    for item in map(dict, d['entries']):
        item['item_type'] = item_type
        item['couch_lifestream_date'] = datetime.datetime.fromtimestamp(
            time.mktime(item['updated_parsed']))
        if len(db.query(map_fun, key=item[discriminator])) == 0:
            for (key, val) in item.items():
                if 'parsed' in key:
                    del item[key]
                elif isinstance(val, datetime.datetime):
                    item[key] = val.isoformat()
                elif isinstance(val, datetime.date):
                    item[key] = val.isoformat()
            db.create(item)
    print "%s items fetched" % (item_type,)

### PER-SERVICE FUNCTIONS ###

def fetch_twitter_items():
    from dateutil.parser import parse
    def callback(item):
        item['couch_lifestream_date'] = parse(item['created_at']).isoformat()
        return item
    url = 'http://twitter.com/statuses/user_timeline.json?id=%s' % (TWITTER_USERNAME,)
    parse_json(url, 'twitter', callback)

POWNCE_USERNAME = getattr(settings, 'POWNCE_USERNAME', None)

def fetch_pownce_items():
    url = 'http://api.pownce.com/2.0/note_lists/%s.json' % (POWNCE_USERNAME,)
    def callback(item):
        y, month, d, h, m, s, wd, jd, ds = time.gmtime(item['timestamp'])
        couch_lifestream_date = datetime.datetime(y, month, d, h, m, s)
        item['couch_lifestream_date'] = couch_lifestream_date.isoformat()
        return item
    parse_json(url, 'pownce', callback, list_key='notes')

REDDIT_USERNAME = getattr(settings, 'REDDIT_USERNAME', None)

def fetch_reddit_items():
    reddit_like_url = 'http://www.reddit.com/user/%s/liked/.rss' % (REDDIT_USERNAME,)
    parse_feed(reddit_like_url, 'reddit-like', discriminator='link')
    reddit_bookmark_url = 'http://www.reddit.com/user/%s/submitted/.rss' % (REDDIT_USERNAME,)
    parse_feed(reddit_bookmark_url, 'reddit-bookmark', discriminator='link')
    reddit_comment_url = 'http://www.reddit.com/user/%s/comments/.rss' % (REDDIT_USERNAME,)
    parse_feed(reddit_comment_url, 'reddit-comment', discriminator='link')

FLICKR_USER_ID = getattr(settings, 'FLICKR_USER_ID', None)

def fetch_flickr_items():
    flickr_url = 'http://api.flickr.com/services/feeds/photos_public.gne?format=atom&id=%s' % (FLICKR_USER_ID,)
    parse_feed(flickr_url, 'flickr')

GITHUB_USERNAME = getattr(settings, 'GITHUB_USERNAME', None)

def fetch_github_items():
    github_url = 'http://github.com/%s.atom' % (GITHUB_USERNAME,)
    parse_feed(github_url, 'github')

DIGG_USERNAME = getattr(settings, 'DIGG_USERNAME', None)

def fetch_digg_items():
    digg_digg_url = 'http://digg.com/users/%s/history/diggs.rss' % (DIGG_USERNAME,)
    parse_feed(digg_digg_url, 'digg-digg', discriminator='link')
    digg_comment_url = 'http://digg.com/users/%s/history/comments.rss' % (DIGG_USERNAME,)
    parse_feed(digg_comment_url, 'digg-comment', discriminator='link')
    digg_bookmark_url = 'http://digg.com/users/%s/history/submissions.rss' % (DIGG_USERNAME,)
    parse_feed(digg_bookmark_url, 'digg-bookmark', discriminator='link')

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
        if GITHUB_USERNAME is not None:
            fetch_github_items()
        if DIGG_USERNAME is not None:
            fetch_digg_items()
        print "Finished loading lifestream items."