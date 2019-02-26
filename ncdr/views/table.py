from django.http import Http404, JsonResponse
from django.views.generic import DetailView, View

from ..models import Database, Table


class TableAPI(View):
    """An API to generate Table data in the format Select2 requires it."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        tables = Table.objects.filter(
            schema__version=request.version,
            schema__database_id=self.kwargs["database_pk"],
        ).values("pk", "name")

        # translate dicts to the preferred shape for Select2
        tables = [{"id": str(t["pk"]), "text": t["name"]} for t in tables]

        return JsonResponse(list(tables), safe=False)


class TableDetail(DetailView):
    model = Table
    template_name = "table_detail.html"

    def get_context_data(self, **kwargs):
        # get the list of tables in this database
        context = super().get_context_data(**kwargs)
        context["tables"] = self.object.schema.tables.all()
        return context

    def get_queryset(self):
        try:
            database = self.request.version.databases.get(name=self.kwargs["db_name"])
        except Database.DoesNotExist:
            raise Http404

        return (
            super()
            .get_queryset()
            .filter(schema__database=database)
            .filter(pk=self.kwargs["pk"])
        )
