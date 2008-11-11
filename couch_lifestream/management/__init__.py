from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from couch_lifestream import models, db, COUCHDB_DESIGN_DOCNAME
from couchdb.design import ViewDefinition
from textwrap import dedent
from django.conf import settings

item_type_date = ViewDefinition(COUCHDB_DESIGN_DOCNAME, 'item_type_date',
    dedent("""
    function(doc) {
        emit([doc.item_type, doc.couch_lifestream_date], null);
    }
"""))

by_date = ViewDefinition(COUCHDB_DESIGN_DOCNAME, 'by_date',
    dedent("""
    function(doc) {
        emit(doc.couch_lifestream_date, null);
    }
"""))

def create_couchdb_views(app, created_models, verbosity, **kwargs):
    ViewDefinition.sync_many(db, [item_type_date, by_date])
    ContentType.objects.get_or_create(
        name='CouchDB Item',
        app_label='couch_lifestream',
        model='couchdbitem'
    )
signals.post_syncdb.connect(create_couchdb_views, sender=models)