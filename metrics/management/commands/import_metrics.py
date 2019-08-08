import csv

from django.core.management.base import BaseCommand

from ...models import Metric, MetricLead, Operand, Organisation, Report, TeamLead, Topic


class Row:
    def __init__(self, row):
        self.row = row

    def operand(self, operand_type):
        mapping = {
            "": "value",
            "source": "source",
            "source address": "source_address",
            "lowest level of granularity of data": "lowest_level_granularity",
            "frequency of data": "frequency",
            "timeliness of data": "timeliness",
            "refresh mechanism": "refresh_mechanism",
        }
        lookup = {"type": operand_type}
        for k, v in mapping.items():
            lookup_key = f"{operand_type} {k}".strip()
            lookup[v] = self.row[lookup_key]
        operand, _ = Operand.objects.get_or_create(**lookup)
        return operand

    def get_associated(self, model, name):
        if self.row[name] and self.row[name].strip():
            result, _ = model.objects.get_or_create(name=self.row[name])
            return result

    def numerator(self):
        return self.operand("Numerator")

    def denominator(self):
        return self.operand("Denominator")

    def topics(self):
        topic_names = [i.strip() for i in self.row["Topic"].split(";")]
        result = []
        for topic_name in topic_names:
            if topic_name:
                topic, _ = Topic.objects.get_or_create(name=topic_name)
                result.append(topic)
        return result

    def organisation_owner(self):
        return self.get_associated(Organisation, "Organisation owner")

    def report(self):
        return self.get_associated(Report, "Report")

    def team_lead(self):
        return self.get_associated(TeamLead, "Team lead")

    def metric_lead(self):
        return self.get_associated(MetricLead, "Metric lead")

    def create_metric(self):
        mapping = {
            "Metric ID": "upstream_id",
            "Display name": "display_name",
            "Indicator / Metric": "indicator",
            "Business definition": "definition",
            "Rationale": "rationale",
            "Technical specification": "specification",
            "Publication Status": "publication_status",
            "Calculation of metric": "calculation",
            "Comments": "comments",
            "Strategic Origin": "strategic_origin",
            "Inidcator Type": "indicator_type",
            "Organisation Type": "organisation_type",
        }

        metric = Metric()

        for k, v in mapping.items():
            setattr(metric, v, self.row[k])

        fks = [
            "numerator",
            "denominator",
            "organisation_owner",
            "report",
            "team_lead",
            "metric_lead",
        ]

        for fk in fks:
            fk_instance = getattr(self, fk)()
            if fk_instance:
                setattr(metric, fk, fk_instance)
        metric.save()
        metric.topics.add(*self.topics())
        return metric


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        Metric.objects.all().delete()
        with open(options["path"], "r", encoding="ISO-8859-1") as f:
            rows = list(csv.DictReader(f, delimiter="¬"))
            for csv_row in rows:
                row = Row(csv_row)
                row.create_metric()

        self.stdout.write(self.style.SUCCESS("Added Metrics"))
