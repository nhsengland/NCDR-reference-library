from django.db.models import Prefetch
from django.http import Http404
from django.views.generic import ListView

from ..models import Column, DataElement, Grouping


class GroupingDetail(ListView):
    model = DataElement
    paginate_by = 50
    template_name = "grouping_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = (
                Grouping.objects.filter(
                    dataelement__column__table__schema__database__version=request.ncdr_version
                )
                .distinct()
                .get(slug=self.kwargs["slug"])
            )
        except Grouping.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grouping"] = self.object
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                column__table__schema__database__version=self.request.ncdr_version,
                grouping=self.object,
            )
            .prefetch_related(
                Prefetch(
                    "column_set",
                    queryset=Column.objects.filter(
                        table__schema__database__version=self.request.ncdr_version
                    ),
                )
            )
            .distinct()
        )


class GroupingList(ListView):
    model = Grouping
    template_name = "grouping_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                dataelement__column__table__schema__database__version=self.request.ncdr_version
            )
            .distinct()
        )
