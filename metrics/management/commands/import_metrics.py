import csv
import io

from django.core.management.base import BaseCommand

from ...models import Lead, Metric, Operand, Organisation, Report, Team


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def build_operand(self, row, type):
        label = type.capitalize()

        def get(name):
            return row[f"{label} {name}"]

        operand, _ = Operand.objects.get_or_create(
            type=type,
            value=row[label],
            source=get("source"),
            source_address=get("source address"),
            lowest_level_granularity=get("lowest level of granularity of data"),
            frequency=get("frequency of data"),
            timeliness=get("timeliness of data"),
            refresh_mechanism=get("refresh mechanism"),
        )

        return operand

    def create_metric(
        self, denominator, lead, numerator, organisation, report, team, row
    ):
        return Metric.objects.create(
            denominator=denominator,
            metric_lead=lead,
            numerator=numerator,
            organisation_owner=organisation,
            report=report,
            team_lead=team,
            # theme=theme,
            indicator=row["Indicator / Metric"],
            definition=row["Business definition"],
            rationale=row["Rationale"],
            specification=row["Technical specification"],
            publication_status=row["Publication Status"],
            calculation=row["Calculation of metric"],
            comments=row["Comments"],
        )

    def handle(self, *args, **options):
        Metric.objects.all().delete()
        Report.objects.all().delete()
        Lead.objects.all().delete()
        Team.objects.all().delete()

        with open(options["path"], "rb") as f:
            fd = io.StringIO(f.read().decode("Windows - 1252"))
            rows = list(csv.DictReader(fd, delimiter="¬"))

        for row in rows:
            lead, _ = Lead.objects.get_or_create(name=row["Metric lead"])
            organisation, _ = Organisation.objects.get_or_create(
                name=row["Organisation owner"]
            )
            report, _ = Report.objects.get_or_create(name=row["Report"])
            team, _ = Team.objects.get_or_create(name=row["Team lead"])

            denominator = self.build_operand(row, type="denominator")
            numerator = self.build_operand(row, type="numerator")

            self.create_metric(
                lead=lead,
                organisation=organisation,
                report=report,
                team=team,
                # theme=theme,
                denominator=denominator,
                numerator=numerator,
                row=row,
            )

        self.stdout.write(self.style.SUCCESS("Added Metrics"))
