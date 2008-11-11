from django.conf.urls.defaults import *

urlpatterns = patterns('couch_lifestream.views',
    url(r'^$', 'items', name='clife_index'),
    url(r'^all/$', 'items', name='clife_all'),
    url(r'^service/(?P<service>\S+)/$', 'items', name='clife_service'),
    url(r'^item/(?P<id>\S+)/$', 'item', name='clife_item'),
)