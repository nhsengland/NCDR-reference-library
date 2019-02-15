from django.db.models import Prefetch
from django.http import Http404
from django.views.generic import ListView

from ..models import Column, DataElement, Grouping
from .base import ViewableItems


class GroupingDetail(ViewableItems, ListView):
    model = DataElement
    paginate_by = 50
    template_name = "grouping_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self):
        try:
            return Grouping.objects.viewable(self.request.user).get(
                slug=self.kwargs["slug"]
            )
        except Grouping.DoesNotExist:
            raise Http404

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(grouping=self.object)
            .viewable(self.request.user)
            .prefetch_related(
                Prefetch(
                    "column_set", queryset=Column.objects.viewable(self.request.user)
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grouping"] = self.object
        return context


class GroupingList(ViewableItems, ListView):
    model = Grouping
    template_name = "grouping_list.html"
