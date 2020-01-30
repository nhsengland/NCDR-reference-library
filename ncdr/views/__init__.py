from django.contrib.auth.views import LoginView
from django.http import Http404
from django.views.generic import DetailView

from ..models import Column, Database


class ColumnDetail(DetailView):
    model = Column
    template_name = "column_detail.html"

    def get_queryset(self):
        try:
            database = self.request.ncdr_version.databases.get(
                name=self.kwargs["db_name"]
            )
        except Database.DoesNotExist:
            raise Http404

        return Column.objects.filter(table__schema__database=database)


class Login(LoginView):
    def form_valid(self, form):
        """
        Wipe the users current_version on login so they don't get stale versions
        """
        response = super().form_valid(form)

        self.request.user.current_version = None
        self.request.user.save()

        return response
