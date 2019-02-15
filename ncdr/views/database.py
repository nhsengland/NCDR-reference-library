from django.views.generic import DetailView, ListView

from ..models import Database
from .base import ViewableItems


class DatabaseDetail(ViewableItems, DetailView):
    model = Database
    slug_url_kwarg = "db_name"
    slug_field = "name"
    template_name = "database_detail.html"


class DatabaseList(ViewableItems, ListView):
    model = Database
    template_name = "database_list.html"

    def get_queryset(self):
        """Only show the user their currently selected verison."""
        return super().get_queryset().filter(version=self.request.user.current_version)
