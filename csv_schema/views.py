# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from csv_schema import models
from django.http import HttpResponseRedirect
from django.forms import formset_factory
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import (
    ListView,
    RedirectView,
    DetailView,
    TemplateView,
    UpdateView,
    CreateView,
    DeleteView,
    View
)
from django.urls import reverse
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
        c_models.DataElement,
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


class NCDRDisplay(object):
    """ wraps the normal get queryset to prevent unpublished
        objects being viewable
    """
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        return qs.viewable(self.request.user)


class NCDRFormView(LoginRequiredMixin, NCDRView):
    pass


class NCDRSearchRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        q = self.request.GET.get("q")
        url = None

        if q:
            for p in NCDRView.pertinant:
                if p.objects.search(q, self.request.user).exists():
                    url = reverse(
                        "search",
                        kwargs=dict(
                            model_name=p.get_model_api_name()
                        )
                    )
                    break

        if not url:
            url = reverse(
                "search",
                kwargs=dict(
                    model_name=NCDRView.pertinant[0].get_model_api_name()
                )
            )

        return "{}?{}&search_option={}".format(
            url, self.request.GET.urlencode(), models.SEARCH_OPTIONS[0]
        )


class NCDRSearch(NCDRView, ListView):
    template_name = "search.html"
    paginate_by = 30

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.search(
            self.request.GET["q"],
            self.request.user,
            self.request.GET.get("search_option", models.SEARCH_OPTIONS[0])
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("q")
        user = self.request.user
        ctx["results"] = [
            (i, i.objects.search_count(query, user),) for i in self.pertinant
        ]
        ctx["search_options"] = models.SEARCH_OPTIONS
        ctx["search_count"] = self.model.objects.search_count(
            query, user
        )

        return ctx


class NCDRFormRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # todo, handle what happens if there is no search parameter
        return NCDRView.pertinant[0].get_edit_list_url()


class NCDRAddManyView(NCDRFormView, CreateView):
    template_name = "forms/create.html"

    def get_form(self, *args, **kwargs):
        formset_cls = formset_factory(self.form_class)
        if self.request.POST:
            return formset_cls(self.request.POST)
        else:
            return formset_cls()

    def get_context_data(self, *args, **kwargs):
        ctx = super(NCDRAddManyView, self).get_context_data(*args, **kwargs)
        if "formset" in kwargs:
            ctx["formset"] = kwargs["formset"]
        else:
            ctx["formset"] = self.get_form()
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        formset = form
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    form.save()
            count = len(formset)

            if count == 1:
                display_name = self.model.get_model_display_name()
            else:
                display_name = self.model.get_model_display_name_plural()
            messages.success(
                self.request, '{} {} created.'.format(
                    count,
                    display_name
                )
            )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(formset=form))

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class NCDREditView(NCDRFormView, UpdateView):
    template_name = "forms/update.html"

    def form_valid(self, form):
        result = super(NCDREditView, self).form_valid(form)
        messages.success(
            self.request, '{} updated'.format(
                self.object.get_display_name()
            )
        )
        return result

    def get_success_url(self, *args, **kwargs):
        if "next" in self.request.GET:
            return self.request.GET["next"]
        else:
            return self.model.get_edit_list_url()


class NCDRDeleteView(NCDRFormView, DeleteView):
    template_name = "forms/delete.html"

    def delete(self, *args, **kwargs):
        messages.success(
            self.request, '{} deleted'.format(
                self.get_object().name
            )
        )

        return super().delete(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class NCDREditListView(NCDRFormView, ListView):
    paginate_by = 100
    template_name = "forms/edit_list.html"

    def get_queryset(self):
        return self.model.objects.all()


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return c_models.Database.get_list_url()


class ColumnDetail(NCDRDisplay, DetailView):
    model = models.Column
    template_name = "column_detail.html"


class DatabaseList(NCDRDisplay, ListView):
    model = models.Database
    template_name = "database_list.html"


class DatabaseDetail(NCDRDisplay, DetailView):
    model = models.Database
    slug_url_kwarg = 'db_name'
    slug_field = 'name'
    template_name = "database_detail.html"


class TableDetail(NCDRDisplay, DetailView):
    model = models.Table
    template_name = "table_detail.html"

    def get_object(self, *args, **kwargs):
        return self.get_queryset().get(
            name=self.kwargs["table_name"],
            database__name=self.kwargs["db_name"]
        )

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(TableDetail, self).get_context_data(*args, **kwargs)
        ctx["tables"] = self.object.database.table_set.viewable(
            self.request.user
        )
        return ctx


class DataElementDetail(NCDRDisplay, DetailView):
    model = models.DataElement
    template_name = "data_element_detail.html"


class DataElementList(NCDRDisplay, ListView):
    model = models.DataElement
    template_name = "data_element_list.html"
    NUMERIC = "0-9"
    paginate_by = 50

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        return qs.viewable(self.request.user)


class PublishAll(View, LoginRequiredMixin):
    http_method_names = ["post"]

    def get_success_url(self):
        return self.request.GET["next"]

    def post(self, *args, **kwargs):
        unpublished = models.Column.objects.filter(
            published=False
        )

        unpublished_count = unpublished.count()
        unpublished.update(published=True)
        messages.success(
            self.request, '{} published'.format(
                unpublished_count
            )
        )
        return HttpResponseRedirect(self.get_success_url())


class Publish(View, SingleObjectMixin, LoginRequiredMixin):
    http_method_names = ["post"]
    model = models.Column

    def get_success_url(self):
        return self.request.GET["next"]

    def post(self, *args, **kwargs):
        obj = self.get_object()
        obj.published = bool(kwargs["publish"])
        obj.save()

        if kwargs["publish"]:
            msg = '{} published'.format(
                obj.name
            )
        else:
            msg = '{} unpublished'.format(
                obj.name
            )

        messages.success(
            self.request, msg
        )

        return HttpResponseRedirect(self.get_success_url())


class GroupingList(NCDRDisplay, ListView):
    model = models.Grouping
    template_name = "grouping_list.html"


class GroupingDetail(NCDRDisplay, DetailView):
    model = models.Grouping
    template_name = "grouping_detail.html"

    def get_context_data(self, *args, **kwargs):
        # get the list of tables in this database
        ctx = super(GroupingDetail, self).get_context_data(*args, **kwargs)
        ctx["groupings"] = models.Grouping.objects.viewable(
            self.request.user
        ).order_by('name')
        return ctx


class PreviewModeSwitch(RedirectView):
    """ Switch the preview mode on or off for a user
        gets passed in an integer that we boolerise™
    """
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET["next"]

    def get(self, request, *args, **kwargs):
        user_profile = self.request.user.userprofile
        user_profile.preview_mode = bool(self.kwargs["preview_mode"])
        user_profile.save()
        return super(PreviewModeSwitch, self).get(request, *args, **kwargs)


class UnPublishedList(NCDRFormView, ListView):
    template_name = "forms/unpublished_list.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["object_list"] = ctx["object_list"].filter(
            published=False
        )
        return ctx


class AboutView(TemplateView):
    template_name = "about.html"
