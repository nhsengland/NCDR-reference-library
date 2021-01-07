import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import ColumnImageForm
from ..models import Column, ColumnImage


class ColumnImageList(LoginRequiredMixin, ListView):
    template_name = "column_image_list.html"
    model = ColumnImage
    order_by = "-created"


class ColumnImageCreate(LoginRequiredMixin, CreateView):
    template_name = "column_image_edit.html"
    form_class = ColumnImageForm
    model = ColumnImage
    success_url = reverse_lazy("column_image_list")
    title = "Create column image"


class ColumnImageEdit(LoginRequiredMixin, UpdateView):
    template_name = "column_image_edit.html"
    form_class = ColumnImageForm
    model = ColumnImage
    success_url = reverse_lazy("column_image_list")

    def title(self):
        return f"Edit column image: {self.object.image.name}"


class ColumnPathOptionsList(LoginRequiredMixin, ListView):
    paginate_by = 10
    ordering = (
        "table__schema__database__name",
        "table__schema__name",
        "table__name",
        "name",
    )

    def get_queryset(self):
        qs = Column.objects.filter(table__schema__database__version__is_published=True)
        query_term = self.request.GET.get("q")
        if query_term:
            qs = qs.filter(name__icontains=query_term)

        qs = qs.select_related("table", "table__schema", "table__schema__database")
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        results = []
        for column in ctx["object_list"]:
            table = column.table
            path = [table.schema.database.name, table.schema.name, table.name]
            column_path = path + [column.name]
            results.append(
                {"id": json.dumps(column_path), "text": column.name, "group": path}
            )
        results = sorted(results, key=lambda x: x["text"])
        return {"results": results, "pagination": {"more": ctx["page_obj"].has_next()}}

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
