from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, View

from . import KwargModelMixin
from ..models import Column


class PublishAll(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        unpublished = Column.objects.filter(published=False)
        unpublished_count = unpublished.count()
        unpublished.update(published=True)

        messages.success(self.request, "{} published".format(unpublished_count))

        return redirect(request.GET["next"])


class Unpublished(LoginRequiredMixin, KwargModelMixin, ListView):
    template_name = "forms/unpublished_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(published=False)
