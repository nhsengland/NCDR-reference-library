from unittest import mock
from django.test import TestCase
import datetime
from csv_schema.csv_import import table_loader
from csv_schema import models


class TableLoaderTestCase(TestCase):
    def get_row(self, **kwargs):
        basic_row = {
            '': '',
        'Data End': ' Ongoing',
        'Data Start': 'Apr-15',
        'Database': 'NHSE_IAPT',
        'Date_Range': 'Apr 2015 - Ongoing',
        'Description': 'An appointment is an interaction with a patient by a health care professional with the objective of making a contribution to the health care of the patient. This table holds details of each appointment. A patient may have multiple appointments which require recording.',
        'Link': 'http://content.digital.nhs.uk/iapt',
        'Provisional Schedule': 'TBD',
        'Release schedule': 'TBD',
        'Schema': 'dbo',
        'Table or View': 'Table',
        'Table/View': 'Appointment_v15',
        'Updated Frequency': ''
        }
        basic_row.update(kwargs)
        return basic_row

    def test_process_row_database(self):
        row = self.get_row(**{
            "Table/View": table_loader.NA,
            "Description": "some database",
            "Database": "some name",
            "Link": "http://some_link.com",
            "Schema": ""
        })
        table_loader.process_row(row)
        self.assertFalse(models.Table.objects.exists())
        db = models.Database.objects.get()
        self.assertEqual(
            db.name, 'some name'
        )
        self.assertEqual(
            db.description, "some database"
        )
        self.assertEqual(
            db.link, "http://some_link.com"
        )

    def test_process_row_table_existing_database(self):
        models.Database.objects.create(name='NHSE_IAPT')
        row = self.get_row()
        table_loader.process_row(row)
        table = models.Table.objects.get(name='Appointment_v15')
        self.assertEqual(
            models.Database.objects.get(name='NHSE_IAPT').table_set.get().id,
            table.id
        )
        self.assertEqual(
            table.database.name, 'NHSE_IAPT'
        )
        self.assertEqual(
            table.description,
            'An appointment is an interaction with a patient by a health care \
professional with the objective of making a contribution to the health care of \
the patient. This table holds details of each appointment. A patient may have \
multiple appointments which require recording.'
        )
        self.assertEqual(
            table.link, 'http://content.digital.nhs.uk/iapt'
        )
        self.assertTrue(table.is_table)

    def test_process_row_new_db_table(self):
        row = self.get_row()
        table_loader.process_row(row)
        table = models.Table.objects.get(name='Appointment_v15')
        self.assertEqual(
            models.Database.objects.get(name='NHSE_IAPT').table_set.get().id,
            table.id
        )

    def test_validate_csv_structure_failure(self):
        row = self.get_row()
        row.pop('Database')
        headers = row.keys()
        reader = mock.MagicMock()
        reader.fieldnames = headers
        with self.assertRaises(ValueError) as ve:
            table_loader.validate_csv_structure(reader, "some_file.csv")

        self.assertEqual(
            str(ve.exception), "missing fields Database in some_file.csv"
        )

    def test_validate_csv_structure_success(self):
        row = self.get_row()
        headers = row.keys()
        reader = mock.MagicMock()
        reader.fieldnames = headers
        try:
            table_loader.validate_csv_structure(reader, "some_file.csv")
        except:
            self.fail()

    @mock.patch('csv_schema.csv_import.table_loader.csv')
    @mock.patch('csv_schema.csv_import.table_loader.validate_csv_structure')
    @mock.patch('csv_schema.csv_import.table_loader.process_row')
    def test_load_file(self, process_row, validate_csv_structure, csv):
        m = mock.mock_open()
        csv.DictReader.return_value = ["something"]
        with mock.patch(
            'csv_schema.csv_import.table_loader.open', m, create=True
        ):
            table_loader.load_file("some_file.csv")

        m.assert_called_once_with('some_file.csv')
        csv.DictReader.assert_called_once_with(m.return_value)
        validate_csv_structure.assert_called_once_with(
            ["something"], "some_file.csv"
        )
        process_row.assert_called_once_with("something")
