import json
import pytest
from django_bend.schema import TableSchema, ColumnSchema, MappingSchema, Mapping


class TestMappingSchema:

    def test_simple_create(self):
        schema = MappingSchema([{'from': 1, 'to': True},
                               {'from': 2, 'to': False}])
        assert len(schema.mappings) == 2

    def test_mapping_attrs(self):
        schema = MappingSchema([{'from': 1, 'to': True},
                               {'from': 2, 'to': False}])
        assert schema.mappings[0] == Mapping(1, True)
        assert schema.mappings[1] == Mapping(2, False)

    def test_map_elem_with_match(self):
        schema = MappingSchema([{'from': 1, 'to': True},
                               {'from': 2, 'to': False}])
        assert schema.map_elem(1) == True

    def test_map_elem_without_match(self):
        schema = MappingSchema([{'from': 1, 'to': True},
                               {'from': 2, 'to': False}])
        assert schema.map_elem(3) == 3

class TestColumnSchema:

    def test_create_no_map(self):
        col = ColumnSchema('house', 'core.house')
        assert col.from_name == 'house'
        assert col.to_name == 'core.house'
        assert isinstance(col.mapping, MappingSchema)
        assert len(col.mapping.mappings) == 0

    def test_with_mapping(self):
        col = ColumnSchema('house', 'core.house', [{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        assert isinstance(col.mapping, MappingSchema)
        assert len(col.mapping.mappings) == 2

    def get_target_value_with_mapping(self):
        col = ColumnSchema('house', 'core.house', [{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        assert col.get_target_value(1) == True

    def get_target_value_with_mapping(self):
        col = ColumnSchema('house', 'core.house', [{'from': 1, 'to': True}, {'from': 2, 'to': False}])
        assert col.get_target_value(3) == 3

class TestTableSchema:

    def test_create_no_col_mappings(self):
        data = json.loads('['
                          ' {'
                          '     "from_table": "ftbl_individuals", '
                          '     "to_table": "foo.person", '
                          '     "columns": ['
                          '         {"from": "FirstName", "to": "first_name"}, '
                          '         {"from": "DOB", "to": "date_of_birth"}'
                          '     ]'
                          ' }'
                          ']')[0]
        table = TableSchema.create_from_json(data)
        assert len(table.columns) == 2
        assert table.from_table == 'ftbl_individuals'
        assert table.to_table == 'foo.person'

    def test_create_with_simple_map(self):
        data = json.loads('['
                          ' {'
                          '     "from_table": "ftbl_individuals", '
                          '     "to_table": "foo.person", '
                          '     "columns": '
                          '     ['
                          '         {"from": "FirstName", "to": "first_name"}, '
                          '         {'
                          '             "from": "CanSwim", '
                          '             "to": "can_swim", '
                          '             "mapping": '
                          '             ['
                          '                 {"to": "true", "from": "1"}, '
                          '                 {"to": "false", "from": "2"} '
                          '             ]'
                          '         }'
                          '     ]'
                          ' }'
                          ']')[0]
        table = TableSchema.create_from_json(data)
        assert len(table.columns) == 2

