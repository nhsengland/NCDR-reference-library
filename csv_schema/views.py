# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, RedirectView, TemplateView, View

from . import models

if getattr(settings, "SITE_PREFIX", ""):
    SITE_PREFIX = "/{}".format(settings.SITE_PREFIX.strip("/"))
else:
    SITE_PREFIX = ""


class NCDRDisplay(object):
    """ wraps the normal get queryset to prevent unpublished
        objects being viewable
    """
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        return qs.viewable(self.request.user)


class NCDRFormRedirect(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # todo, handle what happens if there is no search parameter
        return models.Column.get_edit_list_url()


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return models.Database.get_list_url()


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
        return get_object_or_404(
            self.get_queryset(),
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


class PublishAll(View):
    http_method_names = ["post"]

    def get_success_url(self):
        return self.request.GET["next"]

    @method_decorator(login_required)
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


class PreviewModeSwitch(LoginRequiredMixin, RedirectView):
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


class AboutView(TemplateView):
    template_name = "about.html"
