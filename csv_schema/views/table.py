from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, View

from ..models import Table
from .base import ViewableItems


class TableAPI(View):
    """An API to generate Table data in the format Select2 requires it."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        tables = (
            Table.objects.filter(database_id=self.kwargs["database_pk"])
            .viewable(request.user)
            .values("pk", "name")
        )

        # translate dicts to the preferred shape for Select2
        tables = [{"id": str(t["pk"]), "text": t["name"]} for t in tables]

        return JsonResponse(list(tables), safe=False)


class TableDetail(ViewableItems, DetailView):
    model = Table
    template_name = "table_detail.html"

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
            schema__database__name=self.kwargs["db_name"]
        )

    def get_context_data(self, **kwargs):
        # get the list of tables in this database
        context = super().get_context_data(**kwargs)
        context["tables"] = self.object.schema.tables.viewable(self.request.user)
        return context
