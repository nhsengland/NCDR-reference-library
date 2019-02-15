import functools
import operator
import string

from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.views.generic import ListView

from ..models import Column, DataElement
from .base import ViewableItems


class DataElementDetail(ViewableItems, ListView):
    model = Column
    paginate_by = 10
    template_name = "data_element_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = DataElement.objects.viewable(request.user).get(
                slug=self.kwargs["slug"]
            )
        except DataElement.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_element"] = self.object
        return context

    def get_queryset(self):
        return super().get_queryset().filter(data_element=self.object)


class DataElementList(ViewableItems, ListView):
    model = DataElement
    template_name = "data_element_list.html"
    NUMERIC = "0-9"
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset().viewable(self.request.user)

        symbol = self.request.GET.get("letter")

        if not symbol:
            return qs

        if symbol != self.NUMERIC:
            return qs.filter(name__istartswith=symbol[0])

        # handle the 0-9 case
        startswith_args = [Q(name__startswith=str(i)) for i in range(10)]
        return qs.filter(functools.reduce(operator.or_, startswith_args))

    def get_context_data(self, *args, **kwargs):
        symbols = [i for i in string.ascii_uppercase] + [self.NUMERIC]
        other_pages = [
            (symbol, reverse("data_element_list") + f"?letter={symbol}")
            for symbol in symbols
        ]

        context = super().get_context_data(*args, **kwargs)
        context["other_pages"] = other_pages
        return context
