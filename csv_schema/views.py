# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
import functools
from django.db import transaction
from string import ascii_uppercase
from csv_schema import models
from django.http import HttpResponseRedirect
from django.forms import formset_factory
from django.views.generic import (
    ListView,
    RedirectView,
    DetailView,
    TemplateView,
    UpdateView,
    CreateView
)
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.apps import apps
from csv_schema import forms
from csv_schema import models as c_models


if getattr(settings, "SITE_PREFIX", ""):
    SITE_PREFIX = "/{}".format(settings.SITE_PREFIX.strip("/"))
else:
    SITE_PREFIX = ""


class NCDRView(object):
    pertinant = [
        c_models.Column,
        c_models.Table,
        c_models.Database,
        c_models.Mapping,
        c_models.Grouping,
    ]

    @property
    def form_class(self):
        return getattr(forms, "{}Form".format(self.model.__name__))

    @property
    def model(self):
        model = apps.get_model("csv_schema", self.kwargs["model_name"])
        if model not in self.pertinant:
            raise ValueError(
                'We only allow editing of a subset of models {}'.format(
                    self.pertinant
                )
            )
        return model


class NCDRFormRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        result = SITE_PREFIX + reverse(
            'edit_list', kwargs=dict(
                model_name=NCDRView.pertinant[0].__name__.lower()
            )
        )
        return result


class NCDRAddManyView(NCDRView, CreateView):
    template_name = "forms/create.html"

    def get_form(self, *args, **kwargs):
        formset_cls = formset_factory(self.form_class, extra=50)
        if self.request.POST:
            return formset_cls(self.request.POST)
        else:
            return formset_cls()

    def get_context_data(self, *args, **kwargs):
        ctx = super(NCDRAddManyView, self).get_context_data(*args, **kwargs)
        formset_cls = formset_factory(self.form_class, extra=50)
        if self.request.POST:
            ctx["formset"] = formset_cls(self.request.POST)
        else:
            ctx["formset"] = self.get_form()
        ctx["model"] = self.model
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        formset = form
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(formset=form))

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class NCDREditView(NCDRView, UpdateView):
    template_name = "forms/update.html"

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class NCDRDeleteView(NCDRView, UpdateView):
    template_name = "forms/delete.html"

    def get_success_url(self, *args, **kwargs):
        return models.Table.get_edit_list_url()


class NCDREditListView(NCDRView, ListView):
    paginate_by = 100
    template_name = "forms/edit_list.html"

    def get_queryset(self):
        return self.model.objects.all()


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return SITE_PREFIX + reverse('database_list')


class ColumnDetail(DetailView):
    model = models.Column
    template_name = "column_detail.html"


class DatabaseList(ListView):
    model = models.Database
    template_name = "database_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(DatabaseList, self).get_queryset()
        return qs.all_populated()


class DatabaseDetail(DetailView):
    model = models.Database
    slug_url_kwarg = 'db_name'
    slug_field = 'name'
    template_name = "database_detail.html"


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
        return SITE_PREFIX + reverse('ncdr_reference_list', kwargs=dict(letter="A"))


class NcdrReferenceList(ListView):
    model = models.Column
    template_name = "ncdr_reference_list.html"
    NUMERIC = "0-9"
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        references = super(
            NcdrReferenceList, self
        ).get_queryset()

        if self.kwargs["letter"] == self.NUMERIC:
            """ startswith 0, or 1, or 2 etc
            """
            startswith_args = [Q(name__startswith=str(i)) for i in range(10)]
            return references.filter(
                functools.reduce(operator.or_, startswith_args)
        )

        return references.filter(name__istartswith=self.kwargs["letter"][0])

    def get_context_data(self, *args, **kwargs):
        ctx = super(NcdrReferenceList, self).get_context_data(*args, **kwargs)
        symbols = [i for i in ascii_uppercase]
        symbols.append(self.NUMERIC)
        url = lambda x: reverse('ncdr_reference_list', kwargs=dict(letter=x))
        ctx['other_pages'] = ((symbol, SITE_PREFIX + url(symbol),) for symbol in symbols)
        return ctx


class GroupingRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('grouping_detail', kwargs=dict(
            slug=models.Grouping.objects.first().slug)
        )


class GroupingDetail(DetailView):
    model = models.Grouping
    template_name = "grouping_detail.html"

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(GroupingDetail, self).get_context_data(*args, **kwargs)
        ctx["groupings"] = models.Grouping.objects.all().order_by('name')
        return ctx


class AboutView(TemplateView):
    template_name = "about.html"
