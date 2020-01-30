from django.http import Http404
from django.views.generic import DetailView

from ..models import Database, Table


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
            database = self.request.ncdr_version.databases.get(
                name=self.kwargs["db_name"]
            )
        except Database.DoesNotExist:
            raise Http404

        return (
            super()
            .get_queryset()
            .filter(schema__database=database)
            .filter(pk=self.kwargs["pk"])
        )
