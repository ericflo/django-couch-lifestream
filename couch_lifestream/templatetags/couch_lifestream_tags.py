from django import template
from django.template.loader import render_to_string
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

register.tag('display_lifestream_item', do_display_lifestream_item)