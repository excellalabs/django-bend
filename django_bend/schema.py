class TableSchema:

    def __init__(self, from_table, to_table, columns=None):
        self.from_table = from_table
        self.to_table = to_table
        if columns is None:
            self.columns = []
        else:
            self.columns = columns

    @staticmethod
    def create_from_json(table_definition):
        columns = []
        for column in table_definition['columns']:
            if column.get('mapping') is not None:
                columns.append(ColumnSchema(column.get('from'), column.get('to'), column.get('mapping')))
            else:
                columns.append(ColumnSchema(column.get('from'), column.get('to')))
        table_obj = TableSchema(from_table=table_definition['from_table'],
                                to_table=table_definition['to_table'],
                                columns=columns)
        return table_obj

    def get_mapped_values(self, values):
        # Return a copy of the values array, but with column mappings applied
        if len(values) != len(self.columns):
            raise Exception("Length of value array (%d) != number of columns (%d)" % (len(values), len(self.columns)))

        for (column, value) in zip(self.columns, values):
            yield column.get_target_value(value)


class ColumnSchema:

    def __init__(self, from_name, to_name, mapping=None):
        # mapping is expected to be a list of dicts
        self.from_name = from_name
        self.to_name = to_name
        self.mapping = MappingSchema(mapping)

    #def has_mapping(self):
    #    return not self.mapping.empty()

    def get_target_value(self, value):
        return self.mapping.map_elem(value)


class MappingSchema:

    def __init__(self, mapping=None):
        self.mappings = []
        if mapping is not None:
            for maps in mapping:
                self.mappings.append(Mapping(from_value=maps['from'], to_value=maps['to']))

    #def empty(self):
    #    return len(self.mappings) != 0

    def map_elem(self, elem):
        # if a mapping exists, return the mapped value
        # otherwise, return the unmodified value
        for mapping in self.mappings:
            if mapping.from_value == elem:
                return mapping.to_value
        return elem


class Mapping:

    def __init__(self, from_value, to_value):
        self.from_value = from_value
        self.to_value = to_value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
