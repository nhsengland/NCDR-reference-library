from django.test import TestCase
import datetime
from csv_schema.csv_import import column_loader
from csv_schema import models
from unittest import mock


class ColumnLoaderTestCase(TestCase):

    def get_row(self, **kwargs):
        basic_row = {
            "Item_Name": "REFERRAL_ID",
            "Description": "A sequential number allocated to uniquely identify \
a referral record in the reporting period.",
            "Data_Type": "bigint",
            "Is_Derived_Item": "Yes - External",
            "NCDR_Derivation_Methodology": "N/A",
            'Link': 'http://content.digital.nhs.uk/iapt',
            'Author': 'Nathan Abbotts',
            'Present_In_Tables': 'NHSE_IAPT.dbo.Appointment_v15',
            "Created_Date": "11/30/17"
        }
        basic_row.update(kwargs)
        return basic_row

    @mock.patch('csv_schema.csv_import.column_loader.csv')
    @mock.patch('csv_schema.csv_import.column_loader.validate_csv_structure')
    @mock.patch('csv_schema.csv_import.column_loader.process_row')
    def test_load_file(self, process_row, validate_csv_structure, csv):
        m = mock.mock_open()
        csv.DictReader.return_value = ["something"]
        with mock.patch('csv_schema.csv_import.column_loader.open', m, create=True):
            column_loader.load_file("some_file.csv")

        m.assert_called_once_with('some_file.csv')
        csv.DictReader.assert_called_once_with(m.return_value)
        validate_csv_structure.assert_called_once_with(
            ["something"], "some_file.csv"
        )
        process_row.assert_called_once_with("something", "some_file.csv")

    def test_process_row(self):
        row = self.get_row()
        column_loader.process_row(row, "some_file.csv")
        database = models.Database.objects.get(
            name="NHSE_IAPT"
        )
        self.assertEqual(models.Database.objects.count(), 1)
        table = database.table_set.filter(name="Appointment_v15").get()
        self.assertEqual(models.Table.objects.count(), 1)

        self.assertEqual(models.Column.objects.count(), 1)
        column = models.Column.objects.filter(name="REFERRAL_ID").get()
        self.assertEqual(
            column.tables.get(), table
        )
        self.assertEqual(
            column.is_derived_item, True
        )
        self.assertEqual(
            column.derivation, "N/A"
        )
        self.assertEqual(
            column.created_date_ext, datetime.date(2017, 11, 30)
        )
        self.assertEqual(column.description, row["Description"])

    def test_process_row_empty(self):
        self.assertIsNone(column_loader.process_row({}, "some_file_name"))

    def test_validate_csv_structure(self):
        row = self.get_row()
        column_loader.process_row(row, "some_file.csv")
        del row["Present_In_Tables"]
        reader = mock.MagicMock()
        reader.fieldnames = row.keys()

        with self.assertRaises(ValueError) as ve:
            column_loader.validate_csv_structure(reader, "some_file.csv")

        self.assertEqual(
            str(ve.exception),
            "missing fields Present_In_Tables in some_file.csv"
        )

    def test_get_database_to_table_update(self):
        database = models.Database.objects.create(name="some_database")
        models.Table.objects.create(
            name="some_table", database=database
        )
        row = self.get_row(Present_In_Tables="some_database.dbo.some_table")
        result = column_loader.get_database_to_table(row)
        found_database = models.Database.objects.filter(
            name="some_database"
        ).get()
        found_table = models.Table.objects.filter(
            name="some_table"
        ).get()
        self.assertEqual(result[0][0], found_database)
        self.assertEqual(result[0][1], found_table)

    def test_get_database_to_table_error(self):
        row = self.get_row(
            Present_In_Tables="ff.dbo.asdf.dbo.some_table"
        )
        with self.assertRaises(ValueError) as ve:
            column_loader.get_database_to_table(row)
        self.assertEqual(
            str(ve.exception),
            "unable to process db_name and table name for ff.dbo.asdf.dbo.some\
_table"
        )

    def test_get_database_to_table_duplicate(self):
        database = models.Database.objects.create(name="some_database")
        models.Table.objects.create(
            name="some_table", database=database
        )
        row = self.get_row(
            Present_In_Tables="some_database.dbo.some_database.dbo.some_table"
        )
        result = column_loader.get_database_to_table(row)
        found_database = models.Database.objects.filter(
            name="some_database"
        ).get()
        found_table = models.Table.objects.filter(
            name="some_table"
        ).get()
        self.assertEqual(result[0][0], found_database)
        self.assertEqual(result[0][1], found_table)
