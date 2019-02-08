from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..models import Table
from .base import ViewableItems


class TableDetail(ViewableItems, DetailView):
    model = Table
    template_name = "table_detail.html"

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            self.get_queryset(),
            name=self.kwargs["table_name"],
            database__name=self.kwargs["db_name"]
        )

    def get_context_data(self, **kwargs):
        # get the list of tables in this database
        context = super().get_context_data(**kwargs)
        context["tables"] = self.object.database.table_set.viewable(self.request.user)
        return context
