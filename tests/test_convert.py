from django_bend.convert import create_fixture_item, process_table
from django_bend.schema import ColumnSchema, TableSchema, MappingSchema
import pytest
import mock


class TestProcessTable:

    def test_simple_case(self):

        schema = TableSchema(from_table='ftbl_properties',
                             to_table='core.property')
        schema.columns.append(ColumnSchema(from_name="ID", to_name="pk"))
        schema.columns.append(ColumnSchema(from_name="Phone_Number", to_name="phone"))
        schema.columns.append(ColumnSchema(from_name="PropertyAddress", to_name="address"))

        keys = ["ID", "Phone_Number", "PropertyAddress"]
        values = [[1,'(123)456-7890','123 Property Street'],[2,'(098) 765-4321',None],[3,'152-6374','456 Main Street']]

        with mock.patch('django_bend.convert.create_fixture_item') as cfi:
            res = process_table(schema, keys, values)
            # convert rest to a list to exercise the generator
            list(res)

            model = 'core.property'
            keys = ['pk', 'phone', 'address']
            call1 = mock.call(model=model, keys=keys,
                              values=[1, '(123)456-7890', '123 Property Street'])
            call2 = mock.call(model=model, keys=keys,
                              values=[2, '(098) 765-4321', None])
            call3 = mock.call(model=model, keys=keys,
                              values=[3, '152-6374', '456 Main Street'])
            cfi.assert_has_calls([call1, call2, call3])

    def test_simple_mapping(self):
        table = TableSchema(from_table="ftbl_person", to_table="core.person")
        table.columns.append(ColumnSchema(from_name="ID", to_name="pk"))
        table.columns.append(ColumnSchema(from_name="CanSwim", to_name="can_swim",
                                          mapping=[{'from': 1, 'to': 'test'}, {'from': 2, 'to': False}]))

        input_keys = ["ID", "CanSwim"]
        input_values = [[1, 1], [2, 3], [3, 2]]

        with mock.patch('django_bend.convert.create_fixture_item') as cfi:
            res = process_table(table, input_keys, input_values)
            # convert rest to a list to exercise the generator
            list(res)

            model = 'core.person'
            expected_keys = ['pk', 'can_swim']
            expected_values = [[1, 'test'], [2, 3], [3, False]]
            call1 = mock.call(model=model, keys=expected_keys,
                              values=expected_values[0])
            call2 = mock.call(model=model, keys=expected_keys,
                              values=expected_values[1])
            call3 = mock.call(model=model, keys=expected_keys,
                              values=expected_values[2])
            cfi.assert_has_calls([call1, call2, call3])


class TestCreateFixtureItem:

    def test_simple_case(self):
        model="core.property"
        keys=['pk', 'phone', 'description', 'address']
        values=[7, '1234567890', 'Property Name', '123 Property Street']
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street'
            }
        }
        create_fixture_item(model, keys, values) == expected_result

    def test_simple_case_different_order(self):
        model="core.property"
        keys=['phone', 'description', 'pk', 'address']
        values=['1234567890', 'Property Name', 7, '123 Property Street']
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street'
            }
        }
        create_fixture_item(model, keys, values) == expected_result

    def test_no_pk(self):
        model="core.property"
        keys=['phone', 'description', 'address']
        values=['1234567890', 'Property Name', '123 Property Street']
        with pytest.raises(Exception):
            create_fixture_item(model, keys, values)

    def test_with_mapping(self):
        model = "core.property"
        mapping = MappingSchema([{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        keys = {'phone': MappingSchema(), 'description': MappingSchema(),
                'pk': MappingSchema(), 'address': MappingSchema(), 'can_swim': mapping}
        values = ['1234567890', 'Property Name', 7, '123 Property Street', 1]
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street',
                'can_swim': True
            }
        }
        create_fixture_item(model, keys, values) == expected_result

    def test_with_mapping_no_match(self):
        model = "core.property"
        mapping = MappingSchema([{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        keys = {'phone': MappingSchema(), 'description': MappingSchema(),
                'pk': MappingSchema(), 'address': MappingSchema(), 'is_developer': mapping}
        values = ['1234567890', 'Property Name', 7, '123 Property Street', 3]
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street',
                'is_developer': 3
            }
        }
        create_fixture_item(model, keys, values) == expected_result

    def test_with_mapping_already_matched(self):
        model = "core.property"
        mapping = MappingSchema([{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        keys = {'phone': MappingSchema(), 'description': MappingSchema(),
                'pk': MappingSchema(), 'address': MappingSchema(), 'is_developer': mapping}
        values = ['1234567890', 'Property Name', 7, '123 Property Street', False]
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street',
                'is_developer': False
            }
        }
        create_fixture_item(model, keys, values) == expected_result
