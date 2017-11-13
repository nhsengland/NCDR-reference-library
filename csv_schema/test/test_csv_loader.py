from django.test import TestCase
import datetime
from csv_schema import csv_loader
from csv_schema import models
import mock


class CsvLoaderTestCase(TestCase):

    def get_row(self, **kwargs):
        basic_row = {
            "Database": "NHSE_IAPT",
            "Definition ID": "123",
            "Technical check": "something",
            "Table": "Appointment_v15",
            "Data Item": "REFERRAL_ID",
            "Description": "A sequential number allocated",
            "Data type": "bigint",
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
        validate_csv_structure.assert_called_once_with(
            ["something"], "some_file.csv"
        )
        process_row.assert_called_once_with("something", "some_file.csv")

    def test_process_row(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row, 'some_file.csv')
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

        ref = db_row.datadictionaryreference_set.first()

        self.assertEqual(
            ref.name, "ORGANISATION CODE (CODE OF PROVIDER)"
        )

        self.assertEqual(
            ref.link, "http://www.datadictionary.nhs.uk/"
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
        csv_loader.process_row(csv_row, "some_file_name.csv")
        updated_csv_row = self.get_row(
            Description="something different"
        )
        csv_loader.process_row(updated_csv_row, 'some_file.csv')
        db_row = models.Row.objects.get()
        self.assertEqual(
            db_row.description, "something different"
        )

    def test_ignore_unknown_empty_fields(self):
        csv_row = self.get_row(trees="")
        csv_loader.process_row(csv_row, "some_file_name.csv")
        self.assertEqual(
            models.Row.objects.first().data_item, "REFERRAL_ID"
        )

    def test_process_row_raises(self):
        csv_row = self.get_row(trees="are green")

        with self.assertRaises(ValueError) as v:
            csv_loader.process_row(csv_row, "some_file_name.csv")

        self.assertEqual(
            str(v.exception),
            "We are not saving a value for trees in some_file_name.csv, should we be?"
        )

    def test_database_update_new_table(self):
        csv_row = self.get_row()
        csv_loader.process_row(csv_row, "some_file.csv")
        updated_csv_row = self.get_row(Table="something different")
        csv_loader.process_row(updated_csv_row, "some_file_name.csv")
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
        csv_loader.process_row(csv_row, "some_file.csv")
        updated_csv_row = self.get_row(Database="different database")
        csv_loader.process_row(updated_csv_row, "some_file_name.csv")
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
        e = "missing fields Data Dictionary Name, Description, Database, \
Is_Derived_Item, Derivation_Methodology, Data Dictionary Links, Data Item, \
Table, Data type in some_file.csv"
        with self.assertRaises(ValueError) as v:
            csv_loader.validate_csv_structure(mock_reader, 'some_file.csv')

        self.assertEqual(
            str(v.exception), e
        )

    def test_clean_value_strip(self):
        self.assertEqual(csv_loader.clean_value(" hello "), "hello")

    def test_clean_value_unicode(self):
        a = "\xe2\x80\x98O\xe2\x80\x99s"
        self.assertEqual(csv_loader.clean_value(a), u"\u2018O\u2019s")

    def test_process_data_dictionary_reference_multiple(self):
        kwargs = {
            "Data Dictionary Name": "name1 \n name2",
            "Data Dictionary Links": "http://link1.com \n http://link2.com"
        }
        csv_row = self.get_row(**kwargs)
        csv_loader.process_row(csv_row, "some_file.csv")
        row = models.Row.objects.get()
        self.assertEqual(
            row.datadictionaryreference_set.count(), 2
        )
        ref_1 = row.datadictionaryreference_set.all()[0]
        ref_2 = row.datadictionaryreference_set.all()[1]
        self.assertEqual(
            ref_1.name, "name1"
        )
        self.assertEqual(
            ref_1.link, "http://link1.com"
        )

        self.assertEqual(
            ref_2.name, "name2"
        )
        self.assertEqual(
            ref_2.link, "http://link2.com"
        )

    def test_process_data_dictionary_reference_multiple_names_single_link(self):
        kwargs = {
            "Data Dictionary Name": "name1 \n name2",
            "Data Dictionary Links": "http://link1.com \n"
        }
        csv_row = self.get_row(**kwargs)
        csv_loader.process_row(csv_row, "some_file.csv")
        row = models.Row.objects.get()
        self.assertEqual(
            row.datadictionaryreference_set.count(), 2
        )
        ref_1 = row.datadictionaryreference_set.all()[0]
        ref_2 = row.datadictionaryreference_set.all()[1]
        self.assertEqual(
            ref_1.name, "name1"
        )
        self.assertEqual(
            ref_1.link, "http://link1.com"
        )

        self.assertEqual(
            ref_2.name, "name2"
        )
        self.assertEqual(
            ref_2.link, "http://link1.com"
        )

    def test_process_data_dictionary_reference_multiple_names_no_link(self):
        kwargs = {
            "Data Dictionary Name": "name1 \n name2",
            "Data Dictionary Links": ""
        }
        csv_row = self.get_row(**kwargs)
        csv_loader.process_row(csv_row, "some_file_name.csv")
        row = models.Row.objects.get()
        self.assertEqual(
            row.datadictionaryreference_set.count(), 2
        )
        ref_1 = row.datadictionaryreference_set.all()[0]
        ref_2 = row.datadictionaryreference_set.all()[1]
        self.assertEqual(
            ref_1.name, "name1"
        )
        self.assertEqual(
            ref_1.link, None
        )

        self.assertEqual(
            ref_2.name, "name2"
        )
        self.assertEqual(
            ref_2.link, None
        )

    def test_process_data_dictionary_flawed(self):
        kwargs = {
            "Data Dictionary Name": "name1 \n name2 \n name3",
            "Data Dictionary Links": "http://link1.com \n http://link2.com"
        }
        csv_row = self.get_row(**kwargs)
        with self.assertRaises(ValueError) as v:
            csv_loader.process_row(csv_row, "some_file_name.csv")

        self.assertEqual(
            str(v.exception),
            "for NHSE_IAPT.Appointment_v15.REFERRAL_ID the number of links is different"
        )

    def test_process_data_delete_existing(self):
        first_kwargs = {
            "Data Dictionary Name": "name1 \n name2",
            "Data Dictionary Links": "http://link1.com \n http://link2.com"
        }
        csv_row = self.get_row(**first_kwargs)
        csv_loader.process_row(csv_row, "some_file.csv")

        second_kwargs = {
            "Data Dictionary Name": "name3 ",
            "Data Dictionary Links": "http://link3.com"
        }
        csv_row = self.get_row(**second_kwargs)
        csv_loader.process_row(csv_row, "some_file_name.csv")
        data_dictionary_reference = models.DataDictionaryReference.objects.get()
        self.assertEqual(
            data_dictionary_reference.name, "name3"
        )
        self.assertEqual(
            data_dictionary_reference.link, "http://link3.com"
        )
