import functools
import itertools
import operator

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    _user_has_module_perms,
    _user_has_perm,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone

MOST_RECENT = "Most Recent"


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
        return reverse("add_many", kwargs={"model_name": cls.get_model_api_name()})

    @classmethod
    def get_search_url(cls):
        return reverse("search", kwargs={"model_name": cls.get_model_api_name()})

    @classmethod
    def get_create_template(cls):
        return "forms/create/generic_create.html"

    @classmethod
    def get_search_detail_template(cls):
        return "search/{}.html".format(cls.get_model_api_name())

    def get_edit_url(self):
        return reverse("edit", kwargs={"pk": self.id, "model_name": self.get_model_api_name()})

    def get_delete_url(self):
        return reverse("delete", kwargs={"pk": self.id, "model_name": self.get_model_api_name()})

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


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.TextField(null=False, unique=True)
    password = models.TextField(null=True, blank=True)

    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    preview_mode = models.BooleanField(default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    @classmethod
    def get_url_preview_mode_off(cls):
        return reverse("preview_mode", kwargs={"preview_mode": 0})

    @classmethod
    def get_url_preview_mode_on(cls):
        return reverse("preview_mode", kwargs={"preview_mode": 1})

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, module):
        return _user_has_module_perms(self, module)

    def toggle_preview_mode(self):
        """Toggle the preview_mode boolean"""
        self.preview_mode = not self.preview_mode
        self.save()
