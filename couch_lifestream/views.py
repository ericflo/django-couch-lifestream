from couch_lifestream import db, COUCHDB_DESIGN_DOCNAME
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from couchdb import client

def items(request, service=None, extra_context={},
    template='couch_lifestream/list.html'):
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
    context.update(extra_context)
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request)
    )

def item(request, id, extra_context={}, template='couch_lifestream/item.html'):
    try:
        obj = db[id]
    except client.ResourceNotFound:
        raise Http404
    context = {
        'item': obj,
    }
    context.update(extra_context)
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request)
    )