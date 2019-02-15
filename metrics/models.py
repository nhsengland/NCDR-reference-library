from django.db import models
from django.urls import reverse

from ncdr.models import BaseModel, BaseQuerySet


class Lead(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class MetricQueryset(BaseQuerySet):
    def viewable(self, user):
        return self.all()


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
    theme = models.ForeignKey("Theme", on_delete=models.CASCADE, null=True)

    indicator = models.TextField()
    definition = models.TextField()
    rationale = models.TextField()
    specification = models.TextField()

    publication_status = models.TextField()
    calculation = models.TextField()

    comments = models.TextField()

    objects = MetricQueryset.as_manager()

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


class Theme(models.Model):
    number = models.IntegerField()
    name = models.TextField()

    def __str__(self):
        return self.name
