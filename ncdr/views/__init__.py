from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import Http404
from django.urls import reverse
from django.views.generic import DetailView, RedirectView

from ..models import Column, Database


class ColumnDetail(DetailView):
    model = Column
    template_name = "column_detail.html"

    def get_queryset(self):
        try:
            database = self.request.version.databases.get(name=self.kwargs["db_name"])
        except Database.DoesNotExist:
            raise Http404

        return Column.objects.filter(table__schema__database=database)


class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return Database.get_list_url()


class Logout(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        request.user.preview_mode = False
        request.user.save()

        return super().dispatch(request, *args, **kwargs)


class TogglePreviewMode(LoginRequiredMixin, RedirectView):
    """Toggle preview_mode on the current user."""

    def get(self, request, *args, **kwargs):
        request.user.toggle_preview_mode()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return self.request.GET.get("next", reverse("index_view"))
