import functools
import operator
import string

from django.db.models import Prefetch, Q
from django.http import Http404
from django.urls import reverse
from django.views.generic import ListView

from ..models import Column, DataElement


class DataElementDetail(ListView):
    model = Column
    paginate_by = 10
    template_name = "data_element_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = (
                DataElement.objects.filter(
                    column__table__schema__database__version=request.version
                )
                .distinct()
                .get(slug=self.kwargs["slug"])
            )
        except DataElement.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_element"] = self.object
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                table__schema__database__version=self.request.version,
                data_element=self.object,
            )
            .select_related("table__schema__database")
        )


class DataElementList(ListView):
    model = DataElement
    template_name = "data_element_list.html"
    NUMERIC = "0-9"
    paginate_by = 50

    def get_symbol(self):
        return self.request.GET.get("letter", self.get_symbol_options()[0])

    def get_symbol_options(self):
        return [i for i in string.ascii_uppercase] + [self.NUMERIC]

    def get_queryset_for_symbol(self, qs, symbol):
        if symbol != self.NUMERIC:
            return qs.filter(name__istartswith=symbol[0])

        startswith_args = [Q(name__startswith=str(i)) for i in range(10)]
        return qs.filter(functools.reduce(operator.or_, startswith_args))

    def get_context_data(self, *args, **kwargs):
        symbols = self.get_symbol_options()
        qs = self.model.objects.all()
        other_pages = [
            (
                symbol,
                reverse("data_element_list") + f"?letter={symbol}",
                self.get_queryset_for_symbol(qs, symbol).exists(),
            )
            for symbol in symbols
        ]

        context = super().get_context_data(*args, **kwargs)
        context["other_pages"] = other_pages
        context["symbol"] = self.get_symbol()
        return context

    def get_queryset(self):
        columns = Column.objects.filter(
            table__schema__database__version=self.request.version
        )
        qs = (
            super()
            .get_queryset()
            .filter(column__in=columns)
            .prefetch_related(Prefetch("column_set", queryset=columns))
        ).distinct()
        symbol = self.get_symbol()
        return self.get_queryset_for_symbol(qs, symbol)
