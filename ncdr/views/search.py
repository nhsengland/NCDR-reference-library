from django.urls import reverse
from django.views.generic import ListView, RedirectView

from . import KwargModelMixin
from ..models import Column
from ..search import BEST_MATCH, SEARCH_OPTIONS, searchable_models


class Search(KwargModelMixin, ListView):
    template_name = "search.html"
    paginate_by = 30

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.search(
            self.request.GET["q"],
            self.request.user,
            self.request.GET.get("search_option", BEST_MATCH),
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("q")
        user = self.request.user
        ctx["results"] = [
            (i, i.objects.search_count(query, user)) for i in searchable_models
        ]
        ctx["search_options"] = SEARCH_OPTIONS
        ctx["search_count"] = self.model.objects.search_count(query, user)

        return ctx


class SearchRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        q = self.request.GET.get("q")
        url = reverse("search", kwargs={"model_name": Column.get_model_api_name()})

        if q:
            for p in searchable_models:
                if p.objects.search(q, self.request.user).exists():
                    url = reverse(
                        "search", kwargs={"model_name": p.get_model_api_name()}
                    )
                    break

        return f"{url}?{self.request.GET.urlencode()}&search_option={BEST_MATCH}"
