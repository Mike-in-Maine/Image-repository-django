# mikypics/templatetags/lookup.py
from django import template

register = template.Library()

@register.filter
def lookup(dict_data, key):
    return dict_data.get(key)
