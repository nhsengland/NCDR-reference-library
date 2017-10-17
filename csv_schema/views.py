# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView, TemplateView
from csv_schema import models


class RowView(ListView):
    model = models.Row
    paginate_by = 10
    template_name = "row_view.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(RowView, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("database"):
            qs = qs.filter(
                table__database__name=self.request.GET["database"]
            )

        if self.request.GET.get("table"):
            qs = qs.filter(
                table__name=self.request.GET["table"]
            )
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(RowView, self).get_context_data(*args, **kwargs)
        if self.request.GET.get("database"):
            ctx["table_names"] = models.Table.objects.filter(
                database__name=self.request.GET["database"]
            ).values_list("name", flat=True)
        else:
            ctx["table_names"] = models.Table.objects.all().values_list(
                "name", flat=True
            )
        ctx["database_names"] = models.Database.objects.all().values_list(
            'name', flat=True
        )

        return ctx


class AboutView(TemplateView):
    template_name = "about.html"
