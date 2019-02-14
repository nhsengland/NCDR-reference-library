from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    RedirectView,
    UpdateView,
)

from csv_schema import forms
from csv_schema.models import Column, Database, DataElement, Grouping, Table

from .search import BEST_MATCH, SEARCH_OPTIONS

searchable_objects = {
    'column': {
        'model': Column,
        'form': forms.ColumnForm,
        'create_form': forms.CreateColumnForm,
    },
    'table': {
        'model': Table,
        'form': forms.TableForm,
        'create_form': forms.TableForm,
    },
    'database': {
        'model': Database,
        'form': forms.DatabaseForm,
        'create_form': forms.DatabaseForm,
    },
    'dataelement': {
        'model': DataElement,
        'form': forms.DataElementForm,
        'create_form': forms.DataElementForm,
    },
    'grouping': {
        'model': Grouping,
        'form': forms.GroupingForm,
        'create_form': forms.GroupingForm,
    },
}
searchable_models = list(sorted(
    (v["model"] for v in searchable_objects.values()),
    key=lambda m: m.__name__.lower(),
))


class KwargModelMixin(object):
    """
    Mixin to look up a model, form, and create form from a given URL kwarg

    Views using this mixin can avoid defining a model or form_class class
    variable while still inheriting from the Django GCBVs since those will be
    populated via the included properies.
    """
    @property
    def create_form_class(self):
        return self.get_item("create_form")

    @property
    def form_class(self):
        return self.get_item("form")

    def get_item(self, item):
        """
        Get the model name from the URL kwargs and look it up in `searchable_objects`
        """
        info = searchable_objects.get(self.kwargs["model_name"])

        if info is None:
            msg = "We only allow editing of a subset of models {}"
            raise ValueError(msg.format(searchable_models))

        return info[item]

    @property
    def model(self):
        return self.get_item("model")


class AddMany(LoginRequiredMixin, KwargModelMixin, CreateView):
    def get_template_names(self):
        return [self.model.get_create_template()]

    def get_form(self, *args, **kwargs):
        formset_cls = formset_factory(self.form_class)
        if self.request.POST:
            return formset_cls(self.request.POST)
        else:
            return formset_cls()

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        if "formset" in kwargs:
            ctx["formset"] = kwargs["formset"]
        else:
            ctx["formset"] = self.get_form()
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        formset = form
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    form.save()
            count = len(formset)

            if count == 1:
                display_name = self.model.get_model_display_name()
            else:
                display_name = self.model.get_model_display_name_plural()
            messages.success(
                self.request, '{} {} created.'.format(
                    count,
                    display_name
                )
            )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(formset=form))

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class Delete(LoginRequiredMixin, KwargModelMixin, DeleteView):
    template_name = "forms/delete.html"

    def delete(self, *args, **kwargs):
        messages.success(
            self.request, '{} deleted'.format(
                self.get_object().name
            )
        )

        return super().delete(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class Edit(LoginRequiredMixin, KwargModelMixin, UpdateView):
    template_name = "forms/update.html"

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} updated'.format(
                self.object.get_display_name()
            )
        )
        return result

    def get_success_url(self, *args, **kwargs):
        if "next" in self.request.GET:
            return self.request.GET["next"]
        else:
            return self.model.get_edit_list_url()


class List(LoginRequiredMixin, KwargModelMixin, ListView):
    paginate_by = 100
    template_name = "forms/edit_list.html"

    def get_queryset(self):
        return self.model.objects.all()


class Search(KwargModelMixin, ListView):
    template_name = "search.html"
    paginate_by = 30

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.search(
            self.request.GET["q"],
            self.request.user,
            self.request.GET.get("search_option", BEST_MATCH)
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("q")
        user = self.request.user
        ctx["results"] = [
            (i, i.objects.search_count(query, user),) for i in searchable_models
        ]
        ctx["search_options"] = SEARCH_OPTIONS
        ctx["search_count"] = self.model.objects.search_count(
            query, user
        )

        return ctx


class SearchRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        q = self.request.GET.get("q")
        url = reverse("search", kwargs={"model_name": Column.get_model_api_name()})

        if q:
            for p in searchable_models:
                if p.objects.search(q, self.request.user).exists():
                    url = reverse("search", kwargs={"model_name": p.get_model_api_name()})
                    break

        return "{}?{}&search_option={}".format(
            url, self.request.GET.urlencode(), BEST_MATCH
        )


class Unpublished(LoginRequiredMixin, KwargModelMixin, ListView):
    template_name = "forms/unpublished_list.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["object_list"] = ctx["object_list"].filter(
            published=False
        )
        return ctx
