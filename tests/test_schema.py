import json

import os
import pytest
from django_bend.schema import TableSchema, ColumnSchema, MappingSchema, Mapping


class TestMappingSchema:

    def test_simple_create(self):
        schema = MappingSchema(map_1={'from': 1, 'to': True},
                               map_2={'from': 2, 'to': False})
        assert len(schema.mappings) == 2

    def test_mapping_attrs(self):
        schema = MappingSchema(map_1={'from': 1, 'to': True},
                               map_2={'from': 2, 'to': False})
        assert schema.mappings[1] == Mapping(1, True)
        assert schema.mappings[0] == Mapping(2, False)


class TestColumnSchema:

    def test_create_no_map(self):
        col = ColumnSchema('house', 'core.house')
        assert len(col.mapping.mappings) == 0

    def test_with_mapping(self):
        col = ColumnSchema('house', 'core.house', map_1={'from': 1, 'to': True},
                           map_2={'from': 2, 'to': False})
        assert len(col.mapping.mappings) == 2


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

    def test_create_with_simple_map(self):
        data = json.loads('['
                          ' {'
                          '     "from_table": "ftbl_individuals", '
                          '     "to_table": "foo.person", '
                          '     "columns": '
                          '     ['
                          '         {"from": "FirstName", "to": "first_name"}, '
                          '         {'
                          '             "from": "IsHomeless", '
                          '             "to": "is_homeless", '
                          '             "mapping": '
                          '             {'
                          '                 "map_1": {"to": "true", "from": "1"}, '
                          '                 "map_2": {"to": "false", "from": "2"} '
                          '             }'
                          '         }, '
                          '     ]'
                          ' }'
                          ']')[0]
        table = TableSchema.create_from_json(data)
        assert table.has_mappings()

