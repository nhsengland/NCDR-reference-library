from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import Http404
from django.urls import reverse
from django.views.generic import DetailView, RedirectView

from ..models import Column, Database
from ..search import searchable_models, searchable_objects


class KwargModelMixin(object):
    """
    Mixin to look up a model, form, and create form from a given URL kwarg

    Views using this mixin can avoid defining a model or form_class class
    variable while still inheriting from the Django GCBVs since those will be
    populated via the included properies.
    """

    @property
    def create_form_class(self):
        return self.get_item("create_form")

    @property
    def form_class(self):
        return self.get_item("form")

    def get_item(self, item):
        """
        Get the model name from the URL kwargs and look it up in `searchable_objects`
        """
        info = searchable_objects.get(self.kwargs["model_name"])

        if info is None:
            raise ValueError(
                f"We only allow editing of a subset of models {searchable_models}"
            )

        return info[item]

    @property
    def model(self):
        return self.get_item("model")


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


class SetLatestVersion(LoginRequiredMixin, RedirectView):
    """Switch version for the current user to the latest Version."""

    def get(self, request, *args, **kwargs):
        request.user.switch_to_latest_version()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return self.request.GET.get("next", reverse("index_view"))


class TogglePreviewMode(LoginRequiredMixin, RedirectView):
    """Toggle preview_mode on the current user."""

    def get(self, request, *args, **kwargs):
        request.user.toggle_preview_mode()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return self.request.GET.get("next", reverse("index_view"))
