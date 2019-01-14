import functools
import itertools
import operator

from django.conf import settings
from django.db import models
from django.urls import reverse

MOST_RECENT = "Most Recent"


def reverse_with_prefix(name, kwargs):
    # TODO: remove this knowledge from the project
    prefix = "/{}".format(settings.SITE_PREFIX.strip("/"))
    return prefix + reverse(name, kwargs=kwargs)


class BaseQuerySet(models.QuerySet):
    def viewable(self, user):
        raise NotImplementedError(
            "we should be implementing a 'viewable' method"
        )

    def search_most_recent(self, search_param, user):
        filters = []
        qs = self.viewable(user)
        for i in self.model.SEARCH_FIELDS:
            field = "{}__icontains".format(i)
            filters.append(models.Q(**{field: search_param}))
        return qs.filter(functools.reduce(operator.or_, filters)).distinct()

    def search_best_match(self, search_param, user):
        qs = self.viewable(user)
        query_results = []
        for i in self.model.SEARCH_FIELDS:
            field = "{}__icontains".format(i)
            query_results.append(qs.filter(**{field: search_param}))
        all_results = itertools.chain(*query_results)
        reviewed = set()

        for i in all_results:
            if i in reviewed:
                continue
            else:
                reviewed.add(i)
                yield i

    def search_count(self, search_param, user):
        return self.search_most_recent(search_param, user).count()

    def search(self, search_param, user, option=MOST_RECENT):
        """ returns all tables that have columns
            we default to MOST_RECENT as querysets are
            more efficient for a lot of operations
        """
        if not search_param:
            return self.none()

        if option == MOST_RECENT:
            return self.search_most_recent(search_param, user)
        else:
            return list(self.search_best_match(search_param, user))


class BaseModel(models.Model):
    @classmethod
    def get_form_display_template(cls):
        return "forms/display_templates/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_form_description_template(cls):
        return "forms/descriptions/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_form_template(cls):
        return "forms/model_forms/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_model_api_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_add_url(cls):
        kwargs = {"model_name": cls.get_model_api_name()}
        return reverse_with_prefix("add_many", kwargs)

    @classmethod
    def get_search_url(cls):
        kwargs = {"model_name": cls.get_model_api_name()}
        return reverse_with_prefix("search", kwargs)

    @classmethod
    def get_create_template(cls):
        return "forms/create/generic_create.html"

    @classmethod
    def get_search_detail_template(cls):
        return "search/{}.html".format(cls.get_model_api_name())

    def get_edit_url(self):
        kwargs = {"pk": self.id, "model_name": self.get_model_api_name()}
        return reverse_with_prefix("edit", kwargs)

    def get_delete_url(self):
        kwargs = {"pk": self.id, "model_name": self.get_model_api_name()}
        return reverse_with_prefix("delete", kwargs)

    def get_display_name(self):
        return self.name

    @classmethod
    def get_model_display_name(cls):
        return cls._meta.verbose_name.title()

    @classmethod
    def get_model_display_name_plural(cls):
        return cls._meta.verbose_name_plural.title()

    @classmethod
    def get_edit_list_url(cls):
        return reverse("edit_list", kwargs={"model_name": cls.get_model_api_name()})

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True
