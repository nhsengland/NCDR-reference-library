import csv

from metrics.models import (
    Metric,
    MetricLead,
    Operand,
    Organisation,
    Report,
    TeamLead,
    Topic,
)


class Row:
    def __init__(self, row, version):
        self.row = row
        self.version = version

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
            if topic_name and not topic_name == "0":
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
            "Inidcator Type": "indicator_type",
            "Organisation Type": "organisation_type",
            "Desired direction": "desired_direction",
        }

        metric = Metric()
        metric.version = self.version

        for k, v in mapping.items():
            setattr(metric, v, self.row[k])

        if not self.row["Strategic Origin"] == "0":
            metric.strategic_origin = self.row["Strategic Origin"]

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


def load_file(fd, version):
    rows = list(csv.DictReader(fd, delimiter="¬"))
    for csv_row in rows:
        row = Row(csv_row, version)
        row.create_metric()
