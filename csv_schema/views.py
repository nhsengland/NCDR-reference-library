# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView, RedirectView, DetailView
from csv_schema import models
from django.core.urlresolvers import reverse
from django.db.models import Count


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('database_list')


class DatabaseList(ListView):
    model = models.Database
    template_name = "database_list.html"


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


class AboutView(ListView):
    model = models.SiteDescription
    template_name = "about.html"
