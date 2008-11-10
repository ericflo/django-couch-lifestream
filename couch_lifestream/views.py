import datetime
from couch_lifestream import db, COUCHDB_DESIGN_DOCNAME
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from couchdb import client

def items(request, service=None):
    kwargs = dict(descending=True)
    if service is None:
        item_type_viewname = '%s/by_date' % (COUCHDB_DESIGN_DOCNAME,)
        lifestream_items = db.view(item_type_viewname, **kwargs)
    else:
        item_type_viewname = '%s/item_type_date' % (COUCHDB_DESIGN_DOCNAME,)
        lifestream_items = db.view(item_type_viewname, **kwargs)[
            [service, "z"]:[service, None]]
    context = {
        'items': list(lifestream_items),
    }
    return render_to_response(
        'couch_lifestream/list.html',
        context,
        context_instance=RequestContext(request)
    )

def item(request, id):
    try:
        obj = db[id]
    except client.ResourceNotFound:
        raise Http404
    context = {
        'item': db[id],
    }
    return render_to_response(
        'couch_lifestream/item.html',
        context,
        context_instance=RequestContext(request)
    )