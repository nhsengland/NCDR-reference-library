from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    _user_has_module_perms,
    _user_has_perm,
)
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from .exceptions import VersionAlreadyExists


def versioned_path(version, filename):
    return f"{version.pk}/{filename}"


class BaseModel(models.Model):
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

    name = models.TextField()
    description = models.TextField(blank=True, default="")
    data_type = models.TextField(choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    # currently the below are not being shown in the template
    # after requirements are finalised we could consider removing them.
    is_derived_item = models.NullBooleanField(
        default=False, verbose_name="Is the item derived?"
    )
    definition_id = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True, null=True)
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

    @cached_property
    def images(self):
        table = self.table
        schema = table.schema
        database = schema.database

        relations = ColumnImageRelation.objects.filter(
            database_name=database.name,
            schema_name=schema.name,
            table_name=table.name,
            column_name=self.name,
        ).select_related("column_image")
        return list(set([i.column_image for i in relations]))

    @property
    def link_display_name(self):
        if self.link:
            stripped = self.link.lstrip("http://").lstrip("https://")
            return stripped.lstrip("www.").split("/")[0]

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
    owner = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["display_name"]
        unique_together = ["name", "version"]
        verbose_name = "Database"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("database_detail", kwargs={"db_name": self.name})

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

    name = models.TextField()
    description = models.TextField(default="")
    slug = models.SlugField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Data Element"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("data_element_detail", kwargs={"slug": self.slug})

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.column_set.first().description


class Grouping(BaseModel, models.Model):
    SEARCH_FIELDS = ["name", "description"]

    name = models.TextField()
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Grouping"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("grouping_detail", kwargs={"slug": self.slug})


class Schema(BaseModel, models.Model):
    name = models.TextField()

    database = models.ForeignKey(
        "Database", on_delete=models.CASCADE, related_name="schemas"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "database"]
        verbose_name = "Schema"

    def __str__(self):
        return self.name


class Table(BaseModel):
    SEARCH_FIELDS = ["name", "description", "link"]

    name = models.TextField()
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(
        verbose_name="Table or View",
        choices=((True, "Table"), (False, "View")),
        default=True,
    )
    date_range = models.TextField(blank=True, default="")

    schema = models.ForeignKey(
        "Schema", on_delete=models.CASCADE, related_name="tables"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "schema"]
        verbose_name = "Table"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {"pk": self.pk, "db_name": self.schema.database.name}
        return reverse("table_detail", kwargs=kwargs)


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


class ColumnImage(models.Model):
    """
    A model contains an image which is then mapped
    to a column of
    {{ database_name }}.{{ schema_name }}.{{ table_name }}.{{ column_name }}

    This is a string mapping based on name because an image
    will show for all columns which map rather than
    being version dependent.
    """

    # We use a file field to allow the user to upload svgs
    image = models.FileField(
        upload_to="imgs",
        validators=[FileExtensionValidator(["gif", "jpg", "jpeg", "png", "svg"])],
        storage=import_string(settings.MEDIA_FILE_STORAGE)(),
    )
    created = models.DateTimeField(default=timezone.now)

    def columns(self):
        result = []
        for relation in self.columnimagerelation_set.all():
            result.append((relation.path(), relation.column_url()))
        return result


class ColumnImageRelation(models.Model):
    created = models.DateTimeField(default=timezone.now)
    column_image = models.ForeignKey("ColumnImage", on_delete=models.CASCADE)
    database_name = models.TextField(default="")
    schema_name = models.TextField(default="")
    table_name = models.TextField(default="")
    column_name = models.TextField(default="")

    class Meta:
        unique_together = [
            "column_image",
            "database_name",
            "schema_name",
            "table_name",
            "column_name",
        ]

    def path(self):
        return f"{self.database_name}.{self.schema_name}{self.table_name}.{self.column_name}"

    def column_url(self):
        column = Column.objects.filter(
            table__schema__database__version__is_published=True,
            table__schema__database__name=self.database_name,
            table__schema__name=self.schema_name,
            table__name=self.table_name,
            name=self.column_name,
        ).first()
        if column:
            return column.get_absolute_url()


class Version(models.Model):
    """Track a related models version number."""

    created_by = models.ForeignKey(
        "User", null=True, on_delete=models.SET_NULL, related_name="versions"
    )

    db_structure = models.FileField(upload_to=versioned_path, null=True)
    definitions = models.FileField(upload_to=versioned_path, null=True)
    grouping_mapping = models.FileField(upload_to=versioned_path, null=True)

    # this is used to mark when a version has finished being processed
    last_process_at = models.DateTimeField(null=True)
    files_hash = models.TextField(null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = "pk"

    def __str__(self):
        return f"Version {self.pk}"

    @transaction.atomic
    def _set_publish_state(self, publish, user):
        previous_published = Version.objects.filter(is_published=True).latest()

        # Unpublish all existing Versions first so we only ever have one
        # version published at a time
        Version.objects.update(is_published=False)

        self.is_published = publish
        self.save()

        VersionAuditLog.objects.create(
            version=self,
            previous_published=previous_published,
            now_published=self,
            created_by=user,
            changed_to_published=publish,
        )

    @classmethod
    def create(
        self, *, db_structure, definitions, grouping_mapping, is_published, created_by
    ):
        """
        Wrap creating a Version with attached files

        The versioned_path function uses the passed Version instance's PK to
        generate the path for uploading files to.  However when creating an
        instance with Version.objects.create we can't guarantee version.pk will
        have been set as the model is not typically saved before the function
        is run.
        """
        contents_hash = md5(
            db_structure.read() + definitions.read() + grouping_mapping.read()
        ).digest()

        # reset file streams after reading them to generate hash
        db_structure.seek(0)
        definitions.seek(0)
        grouping_mapping.seek(0)

        try:
            processed_versions = Version.objects.exclude(last_process_at=None)
            existing_version = processed_versions.get(files_hash=contents_hash)
            raise VersionAlreadyExists(existing_pk=existing_version.pk)
        except Version.DoesNotExist:
            pass

        version = Version.objects.create(
            created_by=created_by, is_published=is_published, files_hash=contents_hash
        )

        version.db_structure = db_structure
        version.definitions = definitions
        version.grouping_mapping = grouping_mapping
        version.save()

        return version

    def publish(self, user):
        self._set_publish_state(True, user)

    def unpublish(self, user):
        self._set_publish_state(False, user)


class VersionAuditLog(models.Model):
    version = models.ForeignKey(
        "Version", on_delete=models.CASCADE, related_name="logs"
    )
    previous_published = models.ForeignKey(
        "Version",
        null=True,
        on_delete=models.SET_NULL,
        related_name="previous_published_versions",
    )
    now_published = models.ForeignKey(
        "Version",
        null=True,
        on_delete=models.SET_NULL,
        related_name="now_published_versions",
    )
    created_by = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="version_logs"
    )

    changed_to_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [
            "created_at",
            "version",
            "previous_published",
            "now_published",
        ]

    def __str__(self):
        return f"Audit Log for Version: {self.version_id}"
