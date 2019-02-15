from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    RedirectView,
    UpdateView,
)

from . import KwargModelMixin
from ..models import Column
from ..search import searchable_models


class SearchableModelsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["searchable_models"] = searchable_models
        return context


class AddMany(LoginRequiredMixin, KwargModelMixin, SearchableModelsMixin, CreateView):
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
            messages.success(self.request, "{} {} created.".format(count, display_name))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(formset=form))

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class Delete(LoginRequiredMixin, KwargModelMixin, SearchableModelsMixin, DeleteView):
    template_name = "forms/delete.html"

    def delete(self, *args, **kwargs):
        messages.success(self.request, "{} deleted".format(self.get_object().name))

        return super().delete(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return self.model.get_edit_list_url()


class Edit(LoginRequiredMixin, KwargModelMixin, SearchableModelsMixin, UpdateView):
    template_name = "forms/update.html"

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, "{} updated".format(self.object.get_display_name())
        )
        return result

    def get_success_url(self, *args, **kwargs):
        if "next" in self.request.GET:
            return self.request.GET["next"]
        else:
            return self.model.get_edit_list_url()


class FormRedirect(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # todo, handle what happens if there is no search parameter
        return Column.get_edit_list_url()


class List(LoginRequiredMixin, KwargModelMixin, SearchableModelsMixin, ListView):
    paginate_by = 100
    template_name = "forms/edit_list.html"

    def get_queryset(self):
        return self.model.objects.all()
