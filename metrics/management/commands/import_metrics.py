import csv

from django.core.management.base import BaseCommand

from ...models import Lead, Metric, Operand, Organisation, Report, Team, Theme


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
        self, denominator, lead, numerator, organisation, report, team, theme, row
    ):
        return Metric.objects.create(
            denominator=denominator,
            metric_lead=lead,
            numerator=numerator,
            organisation_owner=organisation,
            report=report,
            team_lead=team,
            theme=theme,
            indicator=row["Indicator / Metric"],
            definition=row["Business definition"],
            rationale=row["Rationale"],
            specification=row["Technical specification"],
            publication_status=row["Publication Status"],
            calculation=row["Calculation of metric"],
            comments=row["Comments"],
        )

    def get_theme(self, number):
        try:
            number = int(number)
        except ValueError:
            return None

        theme, _ = Theme.objects.get_or_create(number=number)

        return theme

    def handle(self, *args, **options):
        path = options["path"]

        with open(options["path"], "r") as f:
            delimiter = "\t" if path.endswith(".tsv") else ","
            rows = list(csv.DictReader(f, delimiter=delimiter, quotechar='"'))

        for row in rows:
            lead, _ = Lead.objects.get_or_create(name=row["Metric lead"])
            organisation, _ = Organisation.objects.get_or_create(
                name=row["Organisation owner"]
            )
            report, _ = Report.objects.get_or_create(name=row["Report"])
            team, _ = Team.objects.get_or_create(name=row["Team lead"])
            theme = self.get_theme(row["Theme"])

            denominator = self.build_operand(row, type="denominator")
            numerator = self.build_operand(row, type="numerator")

            self.create_metric(
                lead=lead,
                organisation=organisation,
                report=report,
                team=team,
                theme=theme,
                denominator=denominator,
                numerator=numerator,
                row=row,
            )

        self.stdout.write(self.style.SUCCESS("Added Metrics"))
