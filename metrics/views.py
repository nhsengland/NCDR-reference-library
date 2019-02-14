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
    ordering = "indicator"
    template_name = "metrics-list.html"
