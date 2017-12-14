# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
import functools
from string import ascii_uppercase
from csv_schema import models
from django.views.generic import ListView, RedirectView, DetailView
from django.urls  import reverse
from django.db.models import Q


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('database_list')


class ColumnDetail(DetailView):
    model = models.Column
    template_name = "column_detail.html"


class DatabaseList(ListView):
    model = models.Database
    template_name = "database_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(DatabaseList, self).get_queryset()
        return qs.all_populated()


class DatabaseDetail(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        db = models.Database.objects.get(name=kwargs["db_name"])
        return db.table_set.all_populated().first().get_absolute_url()


class TableDetail(DetailView):
    model = models.Table
    template_name = "table_detail.html"

    def get_object(self, *args, **kwargs):
        return models.Table.objects.get(
            name=self.kwargs["table_name"],
            database__name=self.kwargs["db_name"]
        )

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(TableDetail, self).get_context_data(*args, **kwargs)
        ctx["tables"] = self.object.database.table_set.all_populated()
        return ctx


class NcdrReferenceRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('ncdr_reference_list', kwargs=dict(letter="A"))


class NcdrReferenceList(ListView):
    model = models.Column
    template_name = "ncdr_reference_list.html"
    NUMERIC = "0-9"

    def get_queryset(self, *args, **kwargs):
        references = super(
            NcdrReferenceList, self
        ).get_queryset()

        if self.kwargs["letter"] == self.NUMERIC:
            """ startswith 0, or 1, or 2 etc
            """
            startswith_args = [Q(name__startswith=str(i)) for i in range(10)]
            return references.filter(functools.reduce(operator.or_, startswith_args))

        return references.filter(name__istartswith=self.kwargs["letter"][0])

    def get_context_data(self, *args, **kwargs):
        ctx = super(NcdrReferenceList, self).get_context_data(*args, **kwargs)
        symbols = [i for i in ascii_uppercase]
        symbols.append(self.NUMERIC)
        url = lambda x: reverse('ncdr_reference_list', kwargs=dict(letter=x))
        ctx['other_pages'] = ((symbol, url(symbol),) for symbol in symbols)
        return ctx


class AboutView(ListView):
    model = models.SiteDescription
    template_name = "about.html"
