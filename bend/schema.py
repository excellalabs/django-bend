
class TableSchema:

    def __init__(self, from_table, to_table, columns=[]):
        self.from_table = from_table
        self.to_table = to_table
        self.columns = columns

class ColumnSchema:

    def __init__(self, from_name, to_name, index=None):
        self.from_name = from_name
        self.to_name = to_name
        self.index = index
