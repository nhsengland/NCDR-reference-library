# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView, RedirectView, DetailView
from django.shortcuts import get_object_or_404, get_list_or_404
from csv_schema import models
from django.core.urlresolvers import reverse


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('database_list')


class DatabaseList(ListView):
    model = models.Database
    template_name = "database_list.html"


class DatabaseDetail(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        db = models.Database.objects.get(name=kwargs["db_name"])
        return db.table_set.first().get_absolute_url()


class TableDetail(DetailView):
    model = models.Table
    template_name = "table_detail.html"

    def get_object(self, *args, **kwargs):
        qs = self.get_queryset(*args, **kwargs)
        return get_object_or_404(
            qs,
            name=self.kwargs["table_name"],
            database__name=self.kwargs["db_name"],
            published=True
        )

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(TableDetail, self).get_context_data(*args, **kwargs)
        ctx["tables"] = self.object.database.table_set.published()
        return ctx


class AboutView(ListView):
    model = models.SiteDescription
    template_name = "about.html"


class AdminTablesVersionRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tables = models.Table.objects.filter(
            database__name=kwargs["db_name"],
            name=kwargs["table_name"]
        )
        published_table = tables.filter(published=True).first()
        if published_table:
            return published_table.get_versions_url()

        return tables.first().get_versions_url()


class AdminTablesVersions(DetailView):
    model = models.Table
    template_name = "table_versions.html"

    def get_object(self, *args, **kwargs):
        qs = self.get_queryset(*args, **kwargs)
        return get_object_or_404(
            qs,
            database__name=self.kwargs["db_name"],
            name=self.kwargs["table_name"],
            version=self.kwargs["version"]
        )

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(AdminTablesVersions, self).get_context_data(
            *args, **kwargs
        )
        ctx["tables"] = models.Table.objects.filter(
            database__name=self.kwargs["db_name"],
            name=self.kwargs["table_name"]
        )
        ctx["name"] = self.kwargs["table_name"]
        ctx["db_name"] = self.kwargs["db_name"]
        return ctx


class AdminTablesEdit(DetailView):
    model = models.Table
    template_name = "table_edit.html"

    def get_object(self, *args, **kwargs):
        qs = self.get_queryset(*args, **kwargs)
        return get_object_or_404(
            qs,
            database__name=self.kwargs["db_name"],
            name=self.kwargs["table_name"],
            version=self.kwargs["version"]
        )


class AdminTablesVersionPreview(TableDetail):
    model = models.Table

    def get_object(self, *args, **kwargs):
        qs = self.get_queryset(*args, **kwargs)
        return get_object_or_404(
            qs,
            name=self.kwargs["table_name"],
            database__name=self.kwargs["db_name"],
            version=self.kwargs["version"]
        )

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(TableDetail, self).get_context_data(*args, **kwargs)
        ctx["tables"] = self.object.database.table_set.all()
        return ctx
