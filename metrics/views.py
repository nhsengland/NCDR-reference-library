import functools
import operator
import string

from django.db.models import Count, Q
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from .models import Metric, Topic


class About(TemplateView):
    template_name = "metrics/about.html"


class MetricDetail(DetailView):
    model = Metric
    template_name = "metrics/detail.html"

    def get_queryset(self):
        return (
            self.model.objects.filter(version=self.request.version)
            .select_related(
                "denominator",
                "metric_lead",
                "numerator",
                "organisation_owner",
                "report",
                "team_lead",
            )
            .prefetch_related("topics")
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["topics"] = []

        topics = self.object.topics.all()

        for topic in topics:
            if topic.metric_set.count() > 1:
                ctx["topics"].append(topic)

        return ctx


class AtoZList(ListView):
    model = Metric
    NUMERIC = "0-9"
    paginate_by = 30
    template_name = "metrics/list.html"

    def get_queryset_for_symbol(self, qs, symbol):
        if symbol != self.NUMERIC:
            return qs.filter(display_name__istartswith=symbol[0])

        startswith_args = [Q(display_name__startswith=str(i)) for i in range(10)]
        return qs.filter(functools.reduce(operator.or_, startswith_args))

    def get_context_data(self, *args, **kwargs):
        symbols = [self.NUMERIC] + [i for i in string.ascii_uppercase]
        qs = self.model.objects.all()
        other_pages = [
            (
                symbol,
                reverse("metrics-list") + f"?letter={symbol}",
                self.get_queryset_for_symbol(qs, symbol).exists(),
            )
            for symbol in symbols
        ]

        context = super().get_context_data(*args, **kwargs)
        context["other_pages"] = other_pages
        return context

    def get_queryset(self):
        qs = super().get_queryset().filter(version=self.request.version)
        symbol = self.request.GET.get("letter")

        if not symbol:
            return qs

        return self.get_queryset_for_symbol(qs, symbol)


class TopicList(ListView):
    model = Topic

    def get_queryset(self):
        qs = super().get_queryset().filter(metric__version=self.request.version)
        qs = qs.annotate(metric_count=Count("metric"))
        qs = qs.filter(metric_count__gt=1)
        return qs


class TopicDetail(DetailView):
    model = Topic


class Search(ListView):
    model = Metric
    template_name = "metrics/search.html"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "")
        if not q:
            return Metric.objects.none()
        return (
            qs.filter(version=self.request.version)
            .filter(Q(display_name__icontains=q) | Q(definition__icontains=q))
            .distinct()
        )
