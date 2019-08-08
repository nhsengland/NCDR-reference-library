from django.db import models
from django.urls import reverse

from ncdr.models import BaseModel


class AssociatedModel(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Metric(BaseModel):
    denominator = models.ForeignKey(
        "Operand", on_delete=models.CASCADE, related_name="denominator_metrics"
    )
    numerator = models.ForeignKey(
        "Operand", on_delete=models.CASCADE, related_name="numerator_metrics"
    )
    topics = models.ManyToManyField("Topic")

    organisation_owner = models.ForeignKey("Organisation", on_delete=models.CASCADE)
    report = models.ForeignKey("Report", on_delete=models.CASCADE)
    team_lead = models.ForeignKey(
        "TeamLead", null=True, blank=True, on_delete=models.CASCADE
    )
    metric_lead = models.ForeignKey(
        "MetricLead", null=True, blank=True, on_delete=models.CASCADE
    )

    indicator = models.TextField()
    definition = models.TextField()
    rationale = models.TextField()
    specification = models.TextField()

    publication_status = models.TextField()
    calculation = models.TextField()

    upstream_id = models.TextField(verbose_name="Metric ID")
    display_name = models.TextField()

    PROCESS = "Process"
    STRUCTURE = "Structure"
    OUTCOME = "Outcome"
    INDICATOR_TYPE_CHOICES = (
        (PROCESS, PROCESS),
        (STRUCTURE, STRUCTURE),
        (OUTCOME, OUTCOME),
    )

    indicator_type = models.TextField(choices=INDICATOR_TYPE_CHOICES)

    comments = models.TextField()

    class Meta:
        verbose_name = "Metric"

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse("metrics-detail", kwargs={"pk": self.pk})


class Topic(AssociatedModel):
    pass


class Organisation(AssociatedModel):
    pass


class Report(AssociatedModel):
    pass


class TeamLead(AssociatedModel):
    pass


class MetricLead(AssociatedModel):
    pass


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
