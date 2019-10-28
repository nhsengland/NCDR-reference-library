from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from ncdr.models import BaseModel


class Lead(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Metric(BaseModel):
    SEARCH_FIELDS = ["indicator"]

    denominator = models.ForeignKey(
        "Operand", on_delete=models.CASCADE, related_name="denominator_metrics"
    )
    metric_lead = models.ForeignKey("Lead", on_delete=models.CASCADE)
    numerator = models.ForeignKey(
        "Operand", on_delete=models.CASCADE, related_name="numerator_metrics"
    )
    organisation_owner = models.ForeignKey("Organisation", on_delete=models.CASCADE)
    report = models.ForeignKey("Report", on_delete=models.CASCADE)
    team_lead = models.ForeignKey("Team", on_delete=models.CASCADE)
    indicator = models.TextField()
    definition = models.TextField()
    rationale = models.TextField()
    specification = models.TextField()
    topic_set = models.ManyToManyField("Topic")
    publication_status = models.TextField()
    calculation = models.TextField()

    comments = models.TextField()

    class Meta:
        verbose_name = "Metric"

    def __str__(self):
        return self.indicator

    def get_absolute_url(self):
        return reverse("metrics-detail", kwargs={"pk": self.pk})


class Operand(models.Model):
    type = models.TextField(
        choices=[("denominator", "denominator"), ("numerator", "numerator")]
    )
    value = models.TextField()
    source = models.TextField()
    source_address = models.TextField()
    lowest_level_granularity = models.TextField()
    frequency = models.TextField()
    timeliness = models.TextField()
    refresh_mechanism = models.TextField()

    class Meta:
        unique_together = (
            "type",
            "value",
            "source",
            "source_address",
            "lowest_level_granularity",
            "frequency",
            "timeliness",
            "refresh_mechanism",
        )

    def __str__(self):
        return f"{self.type}: {self.source}"


class Organisation(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Report(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.TextField(unique=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("topics-detail", kwargs={"slug": self.slug})
