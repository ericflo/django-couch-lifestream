from couchdb import client
from django.conf import settings

class CouchDBImproperlyConfigured(Exception):
    pass

try:
    HOST = settings.COUCHDB_HOST
except AttributeError:
    raise CouchDBImproperlyConfigured("Please ensure that COUCHDB_HOST is " +
        "set in your settings file.")

DATABASE_NAME = getattr(settings, 'COUCHDB_DATABASE_NAME', 'couch_lifestream')
COUCHDB_DESIGN_DOCNAME = getattr(settings, 'COUCHDB_DESIGN_DOCNAME',
    'couch_lifestream-design')

TWITTER_USERNAME = getattr(settings, 'TWITTER_USERNAME', None)
POWNCE_USERNAME = getattr(settings, 'POWNCE_USERNAME', None)
REDDIT_USERNAME = getattr(settings, 'REDDIT_USERNAME', None)
FLICKR_USER_ID = getattr(settings, 'FLICKR_USER_ID', None)
GITHUB_USERNAME = getattr(settings, 'GITHUB_USERNAME', None)
DIGG_USERNAME = getattr(settings, 'DIGG_USERNAME', None)
YOUTUBE_USERNAME = getattr(settings, 'YOUTUBE_USERNAME', None)
LASTFM_USERNAME = getattr(settings, 'LASTFM_USERNAME', None)
PANDORA_USERNAME = getattr(settings, 'PANDORA_USERNAME', None)
READERNAUT_USERNAME = getattr(settings, 'READERNAUT_USERNAME', None)
DELICIOUS_USERNAME = getattr(settings, 'DELICIOUS_USERNAME', None)
DISQUS_USERNAME = getattr(settings, 'DISQUS_USERNAME', None)

USERNAMES = dict(
    TWITTER=TWITTER_USERNAME,
    POWNCE=POWNCE_USERNAME,
    REDDIT=REDDIT_USERNAME,
    FLICKR=FLICKR_USER_ID,
    GITHUB=GITHUB_USERNAME,
    DIGG=DIGG_USERNAME,
    YOUTUBE=YOUTUBE_USERNAME,
    LASTFM=LASTFM_USERNAME,
    PANDORA=PANDORA_USERNAME,
    READERNAUT=READERNAUT_USERNAME,
    DELICIOUS=DELICIOUS_USERNAME,
    DISQUS=DISQUS_USERNAME,
)

server = client.Server(HOST)

try:
    db = server.create(DATABASE_NAME)
except (client.ResourceConflict, client.ServerError):
    db = server[DATABASE_NAME]