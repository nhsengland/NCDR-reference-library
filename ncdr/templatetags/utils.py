import more_itertools
from django import template
from django.urls import resolve

register = template.Library()


@register.filter
def chunked(iterable, chunk_size):
    return more_itertools.chunked(iterable, chunk_size)


@register.filter(name="url_name")
def url_name(request):
    return resolve(request.path_info).url_name


@register.filter(name="viewable")
def viewable(query_set, request):
    return query_set.viewable(request.user)
