from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, RedirectView, View

from ..models import Version


class SetLatestVersion(LoginRequiredMixin, RedirectView):
    """Switch version for the current user to the latest Version."""

    def get(self, request, *args, **kwargs):
        request.user.switch_to_latest_version()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return self.request.GET.get("next", reverse("index_view"))


class PublishVersion(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            version = Version.objects.get(pk=self.kwargs["pk"])
        except Version.DoesNotExist:
            raise Http404

        version.is_published = True
        version.save()

        messages.success(request, f"Published Version: {version.pk}")

        return redirect(request.GET.get("next", reverse("index_view")))


class UnpublishedVersions(LoginRequiredMixin, ListView):
    paginate_by = 50
    queryset = Version.objects.filter(is_published=False)
    template_name = "unpublished_list.html"
