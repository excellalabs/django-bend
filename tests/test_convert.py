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
            keys = {'pk': schema.columns[0].mapping, 'phone': schema.columns[1].mapping,
                    'address': schema.columns[2].mapping}
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
        table.columns.append(ColumnSchema(from_name="IsHomeless", to_name="is_homeless",
                                           mapping=[{'from': 1, 'to': True}, {'from': 2, 'to': False}]))

        keys = ["ID", "IsHomeless"]
        values = [[1, 1], [3, 1]]

        with mock.patch('django_bend.convert.create_fixture_item') as cfi:
            res = process_table(table, keys, values)

            list(res)

            model = 'core.person'
            keys = {'pk': table.columns[0].mapping, 'is_homeless': table.columns[1].mapping}
            call1 = mock.call(model=model, keys=keys,
                              values=values[0])
            call2 = mock.call(model=model, keys=keys,
                              values=values[1])
            cfi.assert_has_calls([call1, call2])


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
                'pk': MappingSchema(), 'address': MappingSchema(), 'is_homeless': mapping}
        values = ['1234567890', 'Property Name', 7, '123 Property Street', 1]
        expected_result = {
            'model': 'core.property',
            'pk': 7,
            "fields": {
                'phone': '1234567890',
                'description': 'Property Name',
                'address': '123 Property Street',
                'is_homeless': True
            }
        }
        create_fixture_item(model, keys, values) == expected_result
