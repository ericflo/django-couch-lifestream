from couchdb import client
from django.conf import settings

class CouchDBImproperlyConfigured(Exception):
    pass

try:
    HOST = settings.COUCHDB_HOST
except AttributeError:
    raise CouchDBImproperlyConfigured("Please ensure that COUCHDB_HOST is " + \
        "set in your settings file.")

DATABASE_NAME = getattr(settings, 'COUCHDB_DATABASE_NAME', 'couch_lifestream')
COUCHDB_DESIGN_DOCNAME = getattr(settings, 'COUCHDB_DESIGN_DOCNAME',
    'couch_lifestream-design')

if not hasattr(settings, 'couchdb_server'):
    server = client.Server(HOST)
    settings.couchdb_server = server

if not hasattr(settings, 'couchdb_db'):
    try:
        db = server.create(DATABASE_NAME)
    except client.ResourceConflict:
        db = server[DATABASE_NAME]
    settings.couchdb_db = db