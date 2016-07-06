
class TableSchema:

    def __init__(self, from_table, to_table, columns=[]):
        self.from_table = from_table
        self.to_table = to_table
        self.columns = columns

    @staticmethod
    def create_from_json(table_definition):
        columns = []
        for column in table_definition['columns']:
            columns.append(ColumnSchema(column['from'], column['to']))
        table_obj = TableSchema(from_table=table_definition['from_table'],
                                to_table=table_definition['to_table'],
                                columns=columns)
        return table_obj

class ColumnSchema:

    def __init__(self, from_name, to_name, index=None):
        self.from_name = from_name
        self.to_name = to_name
        self.index = index
