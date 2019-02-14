# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, View

from ..models import Column, Database
from .base import ViewableItems


class ColumnDetail(ViewableItems, DetailView):
    model = Column
    template_name = "column_detail.html"


class FormRedirect(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # todo, handle what happens if there is no search parameter
        return Column.get_edit_list_url()


class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return Database.get_list_url()


class PublishAll(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        unpublished = Column.objects.filter(published=False)
        unpublished_count = unpublished.count()
        unpublished.update(published=True)

        messages.success(self.request, "{} published".format(unpublished_count))

        return redirect(request.GET["next"])


class TogglePreviewMode(LoginRequiredMixin, RedirectView):
    """Toggle preview_mode on the current user."""

    def get(self, request, *args, **kwargs):
        request.user.toggle_preview_mode()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return self.request.GET.get("next", reverse("index_view"))
