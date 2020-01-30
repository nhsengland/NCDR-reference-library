from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, RedirectView, View

from services.rq import queue

from .. import forms
from ..exceptions import VersionAlreadyExists
from ..importers import import_data
from ..models import Version, VersionAuditLog


class AuditLog(LoginRequiredMixin, ListView):
    model = VersionAuditLog
    ordering = "-created_at"
    paginate_by = 30
    template_name = "version_audit_log.html"


class PublishVersion(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            version = Version.objects.get(pk=self.kwargs["pk"])
        except Version.DoesNotExist:
            raise Http404

        with transaction.atomic():
            version.publish(request.user)
            request.user.current_version = None
            request.user.save()

        messages.success(request, f"Version {version.pk} has been published")

        return redirect(request.GET.get("next", reverse("index_view")))


class SwitchToLatestVersion(LoginRequiredMixin, RedirectView):
    """Switch to the given version for the current user."""

    def get(self, request, *args, **kwargs):
        request.user.switch_to_latest_version()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next", reverse("index_view"))


class SwitchToVersion(LoginRequiredMixin, RedirectView):
    """Switch to the given version for the current user."""

    def get(self, request, *args, **kwargs):
        try:
            version = Version.objects.get(pk=self.kwargs["pk"])
        except Version.DoesNotExist:
            raise Http404

        request.user.switch_to_version(version)

        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get("next", reverse("index_view"))


class Timeline(LoginRequiredMixin, ListView):
    template_name = "version_timeline.html"

    def get_queryset(self):
        return VersionAuditLog.objects.filter(now_published=F("version")).order_by(
            "-created_at"
        )


class UnPublishVersion(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            version = Version.objects.get(pk=self.kwargs["pk"])
        except Version.DoesNotExist:
            raise Http404

        if Version.objects.filter(is_published=True).count() < 2:
            messages.info(request, f"You can't unpublish the last published Version")
            return redirect("version_list")

        version.unpublish(request.user)
        messages.success(request, f"Version {version.pk} has been unpublished")

        return redirect(request.GET.get("next", reverse("index_view")))


class UploadNcdr(LoginRequiredMixin, CreateView):
    form_class = forms.UploadNcdrForm
    template_name = "ncdr_version_upload.html"

    @transaction.atomic()
    def form_valid(self, form):
        # create a Version with the files
        try:
            version = Version.create_ncdr(
                db_structure=self.request.FILES["db_structure"],
                definitions=self.request.FILES["definitions"],
                grouping_mapping=self.request.FILES["grouping_mapping"],
                is_published=False,
                created_by=self.request.user,
            )
        except VersionAlreadyExists as e:
            msg = f"These files already exist in Version {e.existing_pk}"
            messages.error(self.request, msg)
            return redirect("version_list")

        # enqueue with RQ
        queue.enqueue(import_data, version.pk)

        messages.info(
            self.request, f"Version {version.pk} has been queued for processing."
        )

        return redirect("version_list")


class VersionList(LoginRequiredMixin, ListView):
    paginate_by = 50
    queryset = Version.objects.order_by("-pk", "-created_at").select_related(
        "created_by"
    )
    template_name = "version_list.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        current_version = Version.objects.get(is_published=True)
        ctx["sub_title"] = f"Current version: {current_version.pk}"
        return ctx
