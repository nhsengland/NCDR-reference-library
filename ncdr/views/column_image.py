from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import ColumnImageForm
from ..models import ColumnImage


class ColumnImageList(ListView):
    template_name = "column_image_list.html"
    model = ColumnImage
    order_by = "-created"


class ColumnImageCreate(CreateView):
    template_name = "column_image_edit.html"
    form_class = ColumnImageForm
    model = ColumnImage
    success_url = reverse_lazy("column_image_list")
    title = "Create column image"


class ColumnImageEdit(UpdateView):
    template_name = "column_image_edit.html"
    form_class = ColumnImageForm
    model = ColumnImage
    success_url = reverse_lazy("column_image_list")

    def title(self):
        return f"Edit column image: {self.object.image.name}"
