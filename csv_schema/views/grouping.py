from django.views.generic import DetailView, ListView

from ..models import Grouping
from .base import ViewableItems


class GroupingDetail(ViewableItems, DetailView):
    model = Grouping
    template_name = "grouping_detail.html"

    def get_context_data(self, **kwargs):
        # get the list of tables in this database
        context = super().get_context_data(**kwargs)
        context["groupings"] = Grouping.objects.viewable(self.request.user).order_by('name')
        return context


class GroupingList(ViewableItems, ListView):
    model = Grouping
    template_name = "grouping_list.html"
