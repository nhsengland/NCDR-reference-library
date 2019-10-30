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


@register.inclusion_tag("template_tags/pagination.html", takes_context=True)
def pagination(context):
    """
    Assumes we are in a list view with a paginator.

    Adds a variable to the context which is the string
    used by the paginator without the page attribute
    so that we can set that ourselves.
    """
    query_dict = context["request"].GET.copy()
    if "page" in query_dict:
        query_dict.pop("page")
    encoded_query = query_dict.urlencode()
    if encoded_query:
        query = f"&{encoded_query}"
    else:
        query = ""
    context["paginator_query_string"] = query
    page_num = context["page_obj"].number
    context["show_elipsis"] = page_num + 5 < context["paginator"].num_pages
    context["additional_pages"] = page_num + 5 <= context["paginator"].num_pages
    return context
