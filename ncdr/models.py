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
from django.utils.functional import cached_property
from django.utils.text import slugify


class BaseModel(models.Model):
    def get_display_name(self):
        return self.name

    @classmethod
    def get_model_display_name(cls):
        return cls._meta.verbose_name.title()

    @classmethod
    def get_model_display_name_plural(cls):
        return cls._meta.verbose_name_plural.title()

    @classmethod
    def get_model_name(cls):
        return cls.__name__.lower()

    @property
    def search_template(self):
        return f"search/{self.__class__.__name__.lower()}.html"

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Column(BaseModel, models.Model):
    DATA_TYPE_CHOICES = (
        ("datetime", "datetime"),
        ("date", "date"),
        ("int", "int"),
        ("bigint", "bigint"),
        ("varchar(1)", "varchar(1)"),
        ("varchar(2)", "varchar(2)"),
        ("varchar(3)", "varchar(3)"),
        ("varchar(4)", "varchar(4)"),
        ("varchar(5)", "varchar(5)"),
        ("varchar(6)", "varchar(6)"),
        ("varchar(7)", "varchar(7)"),
        ("varchar(8)", "varchar(8)"),
        ("varchar(9)", "varchar(9)"),
        ("varchar(10)", "varchar(10)"),
        ("varchar(11)", "varchar(11)"),
        ("varchar(12)", "varchar(12)"),
        ("varchar(13)", "varchar(13)"),
        ("varchar(14)", "varchar(14)"),
        ("varchar(15)", "varchar(15)"),
        ("varchar(16)", "varchar(16)"),
        ("varchar(17)", "varchar(17)"),
        ("varchar(18)", "varchar(18)"),
        ("varchar(19)", "varchar(19)"),
        ("varchar(20)", "varchar(20)"),
        ("varchar(50)", "varchar(50)"),
        ("varchar(100)", "varchar(100)"),
    )
    SEARCH_FIELDS = ["name", "description"]

    data_element = models.ForeignKey(
        "DataElement", on_delete=models.SET_NULL, null=True, blank=True
    )
    table = models.ForeignKey("Table", on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    # currently the below are not being shown in the template
    # after requirements are finalised we could consider removing them.
    technical_check = models.CharField(max_length=255, null=True, blank=True)
    is_derived_item = models.NullBooleanField(
        default=False, verbose_name="Is the item derived?"
    )
    definition_id = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_date_ext = models.DateField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "table", "data_element", "is_derived_item", "link"]
        verbose_name = "Column"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "column_detail",
            kwargs={"db_name": self.table.schema.database.name, "pk": self.pk},
        )

    @property
    def link_display_name(self):
        if self.link:
            stripped = self.link.lstrip("http://").lstrip("https://")
            return stripped.lstrip("www.").split("/")[0]

    @cached_property
    def related(self):
        """
            returns a tuple of (table, columns within the table)
            the column names are sorted alphabetically

            the tables are sorted by database name then name
        """
        other_columns = self.data_element.column_set.exclude(id=self.id)
        other_columns = other_columns.order_by("table__name")
        return other_columns.order_by("table__schema__database__name")

    @cached_property
    def usage_count(self):
        count = self.tables.count()
        if self.data_element:
            count += self.data_element.column_set.count()
        return count


class Database(BaseModel):
    SEARCH_FIELDS = ["display_name", "name", "description", "link"]

    version = models.ForeignKey(
        "Version", on_delete=models.CASCADE, related_name="databases"
    )

    name = models.TextField()
    display_name = models.TextField(blank=True, null=True)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "version"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("database_detail", kwargs={"db_name": self.name})

    @classmethod
    def get_by_name(cls, name, user):
        Database.objects.get

    @classmethod
    def get_list_url(self):
        return reverse("database_list")

    def get_display_name(self):
        return self.display_name

    @property
    def tables(self):
        """
        Get tables for this database

        It's common to want the Tables for a Database but the two models are
        separated by a Schema.  This property aims to simply that lookup.
        """
        return Table.objects.filter(schema__database=self)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace("_", "").title()
        return super().save(*args, **kwargs)


class DataElement(BaseModel, models.Model):
    SEARCH_FIELDS = ["name", "description"]

    grouping = models.ManyToManyField("Grouping")

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("data_element_detail", kwargs={"slug": self.slug})

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.column_set.first().description

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Grouping(BaseModel, models.Model):
    SEARCH_FIELDS = ["name", "description"]

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("grouping_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return super(Grouping, self).save(*args, **kwargs)


class Schema(BaseModel, models.Model):
    name = models.TextField()

    database = models.ForeignKey(
        "Database", on_delete=models.CASCADE, related_name="schemas"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "database"]

    def __str__(self):
        return self.name


class Table(BaseModel):
    SEARCH_FIELDS = ["name", "description", "link"]

    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(
        verbose_name="Table or View",
        choices=((True, "Table"), (False, "View")),
        default=True,
    )
    date_range = models.CharField(max_length=255, blank=True, default="")

    schema = models.ForeignKey(
        "Schema", on_delete=models.CASCADE, related_name="tables"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "schema"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {"pk": self.pk, "db_name": self.schema.database.name}
        return reverse("table_detail", kwargs=kwargs)

    def get_display_name(self):
        return f"{self.schema.database.name} / {self.name}"


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        version = Version.objects.latest()

        user = self.model(email=email, current_version=version, **extra_fields)

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

    current_version = models.ForeignKey("Version", null=True, on_delete=models.SET_NULL)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, module):
        return _user_has_module_perms(self, module)

    def switch_to_latest_version(self):
        """Update this user to the latest published Version"""
        self.current_version = Version.objects.filter(is_published=True).latest()
        self.save()

    def switch_to_version(self, version):
        """Update this user to the given Version"""
        self.current_version = version
        self.save()


class Version(models.Model):
    """Track a related models version number."""

    created_by = models.ForeignKey(
        "User", null=True, on_delete=models.SET_NULL, related_name="versions"
    )

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = "pk"

    def __str__(self):
        return f"Version {self.pk}"
