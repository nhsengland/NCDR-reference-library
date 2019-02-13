from django.http import Http404
from django.views.generic import ListView

from ..models import Column, DataElement
from .base import ViewableItems


class DataElementDetail(ViewableItems, ListView):
    model = Column
    paginate_by = 10
    template_name = "data_element_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = (DataElement.objects.viewable(request.user)
                                              .get(slug=self.kwargs['slug']))
        except DataElement.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_element'] = self.object
        return context

    def get_queryset(self):
        return super().get_queryset().filter(data_element=self.object)


class DataElementList(ViewableItems, ListView):
    model = DataElement
    template_name = "data_element_list.html"
    NUMERIC = "0-9"
    paginate_by = 50
