from django.test import TestCase
import datetime
from csv_schema import csv_loader
from csv_schema import models
import mock


class CsvLoaderTestCase(TestCase):

    def get_row(self, **kwargs):
        basic_row = {
            "Database": "NHSE_IAPT",
            "Definition ID": 123,
            "Technical check": "something",
            "Table_Name": "Appointment_v15",
            "Data_Item_Name": "REFERRAL_ID",
            "Data_Item_Description": "A sequential number allocated",
            "Data_Type": "bigint",
            "Code_(TBC)": "",
            "Code_Description_(TBC)": "",
            "Is_Derived_Item": "Yes",
            "Derivation_Methodology": "Derived as part of a process",
            "Author": "Francis Bacon",
            "Created_Date": "31/08/2017",
            "Data Dictionary Name": "ORGANISATION CODE (CODE OF PROVIDER)",
            "Data Dictionary Links": "http://www.datadictionary.nhs.uk/"
        }
        basic_row.update(kwargs)
        return basic_row

    @mock.patch('csv_schema.csv_loader.csv')
    @mock.patch('csv_schema.csv_loader.validate_csv_structure')
    @mock.patch('csv_schema.csv_loader.process_row')
    def test_load_file(self, process_row, validate_csv_structure, csv):
        m = mock.mock_open()
        csv.DictReader.return_value = ["something"]
        with mock.patch('csv_schema.csv_loader.open', m, create=True):
            csv_loader.load_file("some_file.csv")

        m.assert_called_once_with('some_file.csv')
        csv.DictReader.assert_called_once_with(m.return_value)
        validate_csv_structure.assert_called_once_with(["something"])
        process_row.assert_called_once_with("something")

    def test_process_row(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row)
        self.assertEqual(models.Database.objects.get().name, "NHSE_IAPT")
        self.assertEqual(models.Table.objects.get().name, "Appointment_v15")

        db_row = models.Row.objects.get()

        self.assertEqual(
            db_row.data_item, "REFERRAL_ID"
        )

        self.assertEqual(
            db_row.description, "A sequential number allocated"
        )

        self.assertEqual(
            db_row.data_type, "bigint"
        )

        self.assertEqual(
            db_row.derivation, "Derived as part of a process"
        )

        self.assertEqual(
            db_row.data_dictionary_name, "ORGANISATION CODE (CODE OF PROVIDER)"
        )

        self.assertEqual(
            db_row.data_dictionary_link, "http://www.datadictionary.nhs.uk/"
        )

        self.assertEqual(
            db_row.author, "Francis Bacon"
        )

        self.assertEqual(
            db_row.created_date_ext, datetime.date(2017, 8, 31)
        )

        self.assertEqual(
            db_row.is_derived_item, True
        )

        self.assertEqual(
            db_row.definition_id, 123
        )

        self.assertEqual(
            db_row.technical_check, "something"
        )

    def test_process_row_update(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row)
        updated_csv_row = self.get_row(
            Data_Item_Description="something different"
        )
        csv_loader.process_row(updated_csv_row)
        db_row = models.Row.objects.get()
        self.assertEqual(
            db_row.description, "something different"
        )

    def test_ignore_unknown_empty_fields(self):
        csv_row = self.get_row(trees="")
        csv_loader.process_row(csv_row)
        self.assertEqual(
            models.Row.objects.first().data_item, "REFERRAL_ID"
        )

    def test_process_row_raises(self):
        csv_row = self.get_row(trees="are green")

        with self.assertRaises(ValueError) as v:
            csv_loader.process_row(csv_row)

        self.assertEqual(
            str(v.exception),
            "We are not saving a value for trees, should we be?"
        )

    def test_database_update_new_table(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row)
        updated_csv_row = self.get_row(Table_Name="something different")
        csv_loader.process_row(updated_csv_row)
        self.assertEqual(
            list(models.Table.objects.all().values_list("name", flat=True)),
            ["Appointment_v15", "something different"]
        )
        self.assertEqual(
            models.Table.objects.first().row_set.first().data_item,
            "REFERRAL_ID"
        )

        self.assertEqual(
            models.Table.objects.last().row_set.first().data_item,
            "REFERRAL_ID"
        )

    def test_new_database(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row)
        updated_csv_row = self.get_row(Database="different database")
        csv_loader.process_row(updated_csv_row)
        self.assertEqual(
            list(models.Database.objects.all().values_list("name", flat=True)),
            ["NHSE_IAPT", "different database"]
        )
        self.assertEqual(
            models.Table.objects.first().name,
            "Appointment_v15"
        )

        self.assertEqual(
            models.Table.objects.last().name,
            "Appointment_v15"
        )

    def test_created_date(self):
        self.assertEqual(
            csv_loader.process_created_date("31/08/2017"),
            datetime.date(2017, 8, 31)
        )

    def test_created_date_none(self):
        self.assertEqual(
            csv_loader.process_created_date(""),
            None
        )

    def test_process_is_derived(self):
        self.assertTrue(False)
        self.assertEqual(
            csv_loader.process_is_derived("yes"),
            True
        )

        self.assertEqual(
            csv_loader.process_is_derived("no"),
            False
        )

        self.assertEqual(
            csv_loader.process_is_derived(""),
            None
        )

        with self.assertRaises(ValueError) as v:
            csv_loader.process_is_derived("trees")

        self.assertEqual(
            str(v.exception), "Unable to recognise is derived item trees"
        )

    def test_validate_csv_structure(self):
        mock_reader = mock.MagicMock()
        mock.field_names = ["trees"]
        e = "missing fields Data Dictionary Name, Data_Type, Database, \
Is_Derived_Item, Data_Item_Name, Data_Item_Description, \
Derivation_Methodology, Data Dictionary Links, Table_Name"
        with self.assertRaises(ValueError) as v:
            csv_loader.validate_csv_structure(mock_reader)

        self.assertEqual(
            str(v.exception), e
        )
