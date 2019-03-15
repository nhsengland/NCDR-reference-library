import functools
import itertools
import operator

from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.views.generic import ListView, RedirectView

from metrics.models import Metric

from ..models import Column, Database, DataElement, Grouping, Table

BEST_MATCH = "Best Match"
MOST_RECENT = "Most Recent"
SEARCH_OPTIONS = [BEST_MATCH, MOST_RECENT]

searchableLUT = {
    "column": {"model": Column, "version_link": "table__schema__database__version"},
    "database": {"model": Database, "version_link": "version"},
    "dataelement": {
        "model": DataElement,
        "version_link": "column__table__schema__database__version",
    },
    "grouping": {
        "model": Grouping,
        "version_link": "dataelement__column__table__schema__database__version",
    },
    "metric": {"model": Metric, "version_link": None},
    "table": {"model": Table, "version_link": "schema__database__version"},
}


def best_match(model, qs, search_param):
    queries = (
        qs.filter(**{f"{field}__icontains": search_param}).distinct()
        for field in model.SEARCH_FIELDS
    )
    yield from itertools.chain(*queries)


def most_recent(model, qs, search_param):
    filters = [
        Q(**{f"{field}__icontains": search_param}) for field in model.SEARCH_FIELDS
    ]
    return qs.filter(functools.reduce(operator.or_, filters)).distinct()


def search(model, version, search_param, option=MOST_RECENT):
    """ returns all tables that have columns
        we default to MOST_RECENT as querysets are
        more efficient for a lot of operations
    """
    if not search_param:
        return model.objects.none()

    # Limit results to the current version
    version_link = searchableLUT[model.__name__.lower()]["version_link"]
    qs = model.objects.all()
    if version_link:
        qs = model.objects.filter(**{version_link: version})

    if option == MOST_RECENT:
        return most_recent(model, qs, search_param)

    return list(set(best_match(model, qs, search_param)))


class Search(ListView):
    template_name = "search.html"
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        info = searchableLUT.get(self.kwargs["model_name"])
        if info is None:
            raise Http404

        q = self.request.GET.get("q", "")

        # Required for ListView to function
        self.object_list = search(
            info["model"],
            request.version,
            q,
            self.request.GET.get("search_option", BEST_MATCH),
        )

        models = [x["model"] for x in searchableLUT.values()]
        context = super().get_context_data(**kwargs)
        context["results"] = [
            (model, search(model, request.version, q, option=MOST_RECENT).count())
            for model in models
        ]
        context["search_options"] = SEARCH_OPTIONS
        return self.render_to_response(context)


class SearchRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        q = self.request.GET.get("q")
        url = reverse("search", kwargs={"model_name": "column"})

        full_url = f"{url}?{self.request.GET.urlencode()}&search_option={BEST_MATCH}"

        if not q:
            return full_url

        for model in [x["model"] for x in searchableLUT.values()]:
            if search(model, self.request.version, q, option=MOST_RECENT).exists():
                url = reverse("search", kwargs={"model_name": model.__name__.lower()})
                break
        return full_url
