import re
from django import template
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from couch_lifestream import db
from copy import copy

register = template.Library()

def do_display_lifestream_item(parser, token):
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag must be of format {%% %r ITEM %%}' % (token.contents.split()[0], token.contents.split()[0]))
    if len(split) != 2:
        raise template.TemplateSyntaxError('%r tag must be of format {%% %r ITEM %%}' % (token.contents.split()[0], token.contents.split()[0]))
    return DisplayLifestreamItemNode(split[1])

class DisplayLifestreamItemNode(template.Node):
    def __init__(self, row):
        self.row = template.Variable(row)
    
    def render(self, context):
        row = self.row.resolve(context)
        item = db[row.id]
        context_with_item = copy(context)
        context_with_item['item'] = item
        return render_to_string(
            'couch_lifestream/%s_item.html' % (item['item_type'],),
            context_with_item
        )

def do_get_id_for_doc(parser, token):
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag must be of format {%% %r DOC as CONTEXT_VAR_NAME %%}' % (token.contents.split()[0], token.contents.split()[0]))
    if len(split) != 4:
        raise template.TemplateSyntaxError('%r tag must be of format {%% %r DOC as CONTEXT_VAR_NAME %%}' % (token.contents.split()[0], token.contents.split()[0]))
    return GetIdForDocNode(split[1], split[3])

class GetIdForDocNode(template.Node):
    def __init__(self, doc, context_var):
        self.doc = template.Variable(doc)
        self.context_var = context_var
    
    def render(self, context):
        doc = self.doc.resolve(context)
        context[self.context_var] = doc['_id']
        return ''

TWITTER_RE = re.compile('@(\S+)')

def twitterfy(value):
    return mark_safe(
        TWITTER_RE.sub(r'<a href="http://twitter.com/\1">@\1</a>',value)
    )
twitterfy = stringfilter(twitterfy)

register.tag('display_lifestream_item', do_display_lifestream_item)
register.tag('get_id_for_doc', do_get_id_for_doc)

register.filter('twitterfy', twitterfy)