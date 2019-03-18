import functools
import operator
import string

from django.db.models import Q
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Metric


class MetricDetail(DetailView):
    model = Metric
    template_name = "metric-detail.html"

    def get_queryset(self):
        return self.model.objects.select_related(
            "denominator",
            "metric_lead",
            "numerator",
            "organisation_owner",
            "report",
            "team_lead",
            "theme",
        )


class MetricsList(ListView):
    model = Metric
    NUMERIC = "0-9"
    ordering = "indicator"
    paginate_by = 30
    template_name = "metrics-list.html"

    def get_context_data(self, *args, **kwargs):
        symbols = [i for i in string.ascii_uppercase] + [self.NUMERIC]
        other_pages = [
            (symbol, reverse("metrics-list") + f"?letter={symbol}")
            for symbol in symbols
        ]

        context = super().get_context_data(*args, **kwargs)
        context["other_pages"] = other_pages
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        symbol = self.request.GET.get("letter")

        if not symbol:
            return qs

        if symbol != self.NUMERIC:
            return qs.filter(indicator__istartswith=symbol[0])

        # handle the 0-9 case
        startswith_args = [Q(indicator__startswith=str(i)) for i in range(10)]
        return qs.filter(functools.reduce(operator.or_, startswith_args))
