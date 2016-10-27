class TableSchema:

    def __init__(self, from_table, to_table, columns=[]):
        self.from_table = from_table
        self.to_table = to_table
        self.columns = columns

    @staticmethod
    def create_from_json(table_definition):
        columns = []
        for column in table_definition['columns']:
            columns.append(ColumnSchema(column.get('from'), column.get('to'), column.get('mapping')))
        table_obj = TableSchema(from_table=table_definition['from_table'],
                                to_table=table_definition['to_table'],
                                columns=columns)
        return table_obj

    def has_mappings(self):
        for col in self.columns:
            if col.has_mapping():
                return True

class ColumnSchema:

    def __init__(self, from_name, to_name, index=None, **mapping):
        # **mapping is kwargs of dicts, eg map_1={'from': 1, 'to': true}
        self.from_name = from_name
        self.to_name = to_name
        self.mapping = MappingSchema(**mapping)
        self.index = index

    def has_mapping(self):
        return len(self.mapping.mappings) != 0


class MappingSchema:

    def __init__(self, **mapping):
        self.mappings = []
        for value in mapping.values():
            self.mappings.append(Mapping(from_value=value['from'], to_value=value['to']))


class Mapping:

    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
