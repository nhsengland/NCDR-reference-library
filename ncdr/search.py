from .forms import (
    ColumnForm,
    CreateColumnForm,
    DatabaseForm,
    DataElementForm,
    GroupingForm,
    TableForm,
)
from .models import Column, Database, DataElement, Grouping, Table

BEST_MATCH = "Best Match"
MOST_RECENT = "Most Recent"

SEARCH_OPTIONS = [BEST_MATCH, MOST_RECENT]

searchable_objects = {
    "column": {"model": Column, "form": ColumnForm, "create_form": CreateColumnForm},
    "table": {"model": Table, "form": TableForm, "create_form": TableForm},
    "database": {"model": Database, "form": DatabaseForm, "create_form": DatabaseForm},
    "dataelement": {
        "model": DataElement,
        "form": DataElementForm,
        "create_form": DataElementForm,
    },
    "grouping": {"model": Grouping, "form": GroupingForm, "create_form": GroupingForm},
}
searchable_models = list(
    sorted(
        (v["model"] for v in searchable_objects.values()),
        key=lambda m: m.__name__.lower(),
    )
)
