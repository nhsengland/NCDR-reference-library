from django.http import Http404
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
