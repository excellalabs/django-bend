# -*- coding: utf-8 -*-
# This code is influenced by https://github.com/rstrobl/sqldump-converter

import re
from collections import OrderedDict

# Python3+ zip returns an iterable, use izip for Python2
try:
    from itertools import izip as zip
except ImportError:
    pass # use built-in zip for Python3

from .schema import ColumnSchema
from .parsing import sql_list_splitter, parse_sql_list


def create_fixture_item(model, keys, values):
    # Create a Django Fixture formatted dictionary
    # Input:
    #
    # model: a string value of the fixture model
    # keys: a list of field names
    # values: a list of field values
    #
    # Assumptions:
    #     keys and values are both pre-sorted
    #     one key/value pair is 'pk'
    #
    # Output sample:
    #
    # {
    #   "fields": {
    #     "phone": "1234567890",
    #     "description": "School Name",
    #     "address": "123 School Street",
    #   },
    #   "model": "core.school",
    #   "pk": 7
    # },
    fields = dict(zip(keys, values))
    if 'pk' in fields.keys():
        pk = fields.pop('pk')
    else:
        raise Exception('Expected "pk" as a key in dictionary')

    return {'fields': fields, 'model': model, 'pk': pk}


def get_table_from_dump(tablename, dumpfilename, column_filter=None, offset=None):
    # Pull the requested table from the provided sql dump file
    # Return a 3-tuple:
    #  - line number of the table's insert in sql dump
    #  - list of column names
    #  - list of rows, where each row is a list of values
    #
    # column_filter can be used to return only select columns. The primary
    # key field (`id` or `ID`) will always be returned

    regex = re.compile(r"INSERT INTO [`'\"]%s[`'\"] \((?P<columns>.+)\) VALUES ?(?P<values>.+);" % tablename)

    column_names = []
    rows = []

    with open(dumpfilename, 'r') as dumpfile:
        if offset:
            dumpfile.seek(offset)

        for line_counter, line in enumerate(dumpfile):
            match = regex.match(line)
            if match:

                # Get columns (removing unwanted columns if requested)
                column_names = parse_sql_list(match.group('columns'))
                rows = sql_list_splitter(match.group('values'))

    if column_names and rows:
        # we need to track both column name and index, use OrderedDict
        # to make it easier to align column and value objets
        column_dict = OrderedDict()
        for i,x in enumerate(column_names):
            column_dict[x] = i

        if column_filter:
            for column in column_names:
                # keep primary keys even if not part of filter list
                if column not in column_filter and column not in ['id', 'ID']:
                    del column_dict[column]

        # Filter the columns from the original (pre-filter) column indices
        values_list_of_lists = (parse_sql_list(r, column_filter=column_dict.values()) for r in rows)

        return (line_counter, column_dict.keys(), values_list_of_lists)

    raise Exception("Table `%s` not found in file `%s`" % (tablename, dumpfilename))


def generate_fixture_tables(tableschemas, dumpfilename):
    # Parse requested tables from sql dump
    #
    # Input:
    # tableschemas: an array of TableSchema objects
    # dumpfilename: String value of mysql dump
    #
    # Output:
    # A generator of dicts for each row of each table defined in tableschemas
    # Each dict is in a format prepared to `json.dumps` into a Django Fixture format

    for table in tableschemas:
        old_column_names = [column.from_name for column in table.columns]
        (index, columns, rows) = get_table_from_dump(table.from_table, dumpfilename,
                                                     column_filter=old_column_names)

        # add mapping for primary key
        for count, col in enumerate(columns):
            if col in ['id', 'ID']:
                pk_column = ColumnSchema(from_name=col, to_name='pk')
                table.columns.insert(count, pk_column)
                break
        else:
            raise Exception("Did not find primary key (id or ID) in table %s" % table.from_table)

        # Forward the generator results from process_table
        # Ideally `yield for` would be used here, but that is
        # not python2 compatible
        for item in process_table(table_schema=table,
                                  parsed_column_names=columns,
                                  parsed_rows=rows):
            yield item


def process_table(table_schema, parsed_column_names, parsed_rows):
    # For each row, map the data to the new column names and
    # return a fixture-formatted JSON object

    if len(parsed_column_names) != len(table_schema.columns):
        raise Exception("Unexpected number of columns when parsing table %s. "
                        "Expected %d columns but got %d" % (table_schema.from_table,
                                                            len(table_schema.columns),
                                                            len(parsed_column_names)))

    # Create a list of new table names that align with the order of the
    # parsed rows. Also, ensure all the column names defined actually exist
    new_columns = {}
    for column in table_schema.columns:
        try:
            column_index = parsed_column_names.index(column.from_name)
            new_columns[column_index] = column.to_name
        except ValueError:
            raise Exception("Unrecognized table name: %s:%s" % (table_schema.from_table,
                                                               column.from_name))

    # We can't assume the dict is ordered, so convert the dict to an ordered list
    ordered_new_column_names = [new_columns[x] for x in sorted(new_columns.keys())]

    # convert data to dictionary and append to results
    for values_list in parsed_rows:
        # get a copy of values_list with mappings applied
        mapped_values = table_schema.get_mapped_values(values_list)
        yield create_fixture_item(keys=ordered_new_column_names,
                                  values=list(mapped_values),
                                  model=table_schema.to_table)
