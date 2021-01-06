from collections import defaultdict

from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import ColumnImageForm
from ..models import Column, ColumnImage, Table


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


class ColumnPathOptionsList(ListView):
    paginate_by = 10
    ordering = ("schema__database__name", "schema__name", "name")

    def get_queryset(self):
        qs = Table.objects.filter(schema__database__version__is_published=True)
        query_term = self.request.GET.get("q")
        if query_term:
            column_qs = Column.objects.filter(name__icontains=query_term)
            qs = qs.filter(column__in=column_qs)
        else:
            column_qs = Column.objects.all()
        qs = qs.order_by(*self.ordering)
        qs = qs.prefetch_related(
            Prefetch("column_set", queryset=column_qs, to_attr="our_columns")
        )
        return qs

    def get_path(self, table):
        return ".".join([table.schema.database.name, table.schema.name, table.name])

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        path_to_column = defaultdict(set)
        for table in ctx["object_list"]:
            for column in table.our_columns:
                path_to_column[self.get_path(table)].add(column)
        results = []
        for path, columns in path_to_column.items():
            for column in columns:
                results.append({"id": column.id, "text": column.name, "group": path})
        results = sorted(results, key=lambda x: x["text"])
        return {"results": results, "pagination": {"more": ctx["page_obj"].has_next()}}

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
