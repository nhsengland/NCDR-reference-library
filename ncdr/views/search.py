import functools
import operator

from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import ListView, RedirectView

from ..models import Column, Database, DataElement, Grouping, Table

# from metrics.models import Metric


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
    # "metric": {"model": Metric, "version_link": None},
    "table": {"model": Table, "version_link": "schema__database__version"},
}


def search(model, version, search_param):
    """
    Search the given model at the given version for fields containing the given search parameter

    Version relationship path is looked up from the searchableLUT.

    Build up an OR based query such that searching for "change" would give you:

        Q(name="change") | Q(description="change")

    assuming SEARCH_FIELDS contained "name" and "description".
    """
    if not search_param:
        return model.objects.none()

    # Limit results to the current version
    version_link = searchableLUT[model.__name__.lower()]["version_link"]
    qs = model.objects.all()
    if version_link:
        qs = model.objects.filter(**{version_link: version})

    filters = [
        Q(**{f"{field}__icontains": search_param}) for field in model.SEARCH_FIELDS
    ]
    return qs.filter(functools.reduce(operator.or_, filters)).distinct()


class Search(ListView):
    template_name = "search.html"
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        model_name = self.kwargs["model_name"]

        info = searchableLUT.get(model_name)
        if info is None:
            raise Http404

        q = self.request.GET.get("q", "")

        # Required for ListView to function
        self.object_list = search(info["model"], request.version, q)

        # Get model and result counts
        models = [x["model"] for x in searchableLUT.values()]
        results = [
            {
                "name": model.__name__.lower(),
                "display_name": model._meta.verbose_name_plural,
                "count": search(model, request.version, q).count(),
            }
            for model in models
        ]

        context = super().get_context_data(**kwargs)
        context["results"] = results
        context["model_name"] = model_name
        context["model_display_name"] = info["model"]._meta.verbose_name
        context["model_template"] = f"search/{model_name}.html"
        context["query"] = urlencode({"q": q})
        return self.render_to_response(context)


class SearchRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        q = self.request.GET.get("q")
        url = reverse("search", kwargs={"model_name": "column"})

        full_url = f"{url}?{self.request.GET.urlencode()}"

        if not q:
            return full_url

        for model in [x["model"] for x in searchableLUT.values()]:
            if search(model, self.request.version, q).exists():
                url = reverse("search", kwargs={"model_name": model.__name__.lower()})
                break
        return full_url
