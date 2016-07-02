# -*- coding: utf-8 -*-
# This code is influenced by https://github.com/rstrobl/sqldump-converter

import sys
import getopt
import re
import simplejson as json
from collections import OrderedDict
import itertools

from schema import TableSchema, ColumnSchema
from parsing import sql_list_splitter, parse_into_object_type, parse_sql_list


def create_fixture_item(model, keys, values):
    # Create a Django Fixture formatted dictionary
    # Assumptions:
    #     keys and values are both pre-sorted
    #     one key/value pair is 'id' or 'ID'
    #
    # A Django fixture looks like this:
    #
    # {
    #   "fields": {
    #     "phone": "2025521781",
    #     "description": "School Name",
    #     "address": "123 School Street",
    #   },
    #   "model": "core.school",
    #   "pk": 7
    # },
    fields = dict(itertools.izip(keys, values))
    if 'pk' in fields.keys():
        pk = fields.pop('pk')
    else:
        raise Exception('Expected "pk" as a key in dictionary')

    return {'fields': fields, 'model': model, 'pk': pk} 

def generate_fixture_tables(definition, dumpfilename):
    # we only need the INSERT lines
    regex = re.compile(r"INSERT INTO [`'\"](?P<table>\w+)[`'\"] \((?P<columns>.+)\) VALUES ?(?P<values>.+);")

    with open(dumpfilename, 'r') as dumpfile:
        for line in dumpfile:
            match = regex.match(line)
   
            # If an INSERT statement
            if match:
                table = match.group('table')

                # Check and see if the insert is for one of the defined mapping tables
                for translation_table_obj in definition:
                    if table in translation_table_obj['from_table']:
                        columns = []
                        for column in translation_table_obj['columns']:
                            columns.append(ColumnSchema(column['from'], column['to']))
                        table_obj = TableSchema(from_table=translation_table_obj['from_table'],
                                                to_table=translation_table_obj['to_table'],
                                                columns=columns)
                        
                        # Forward the generator results from process_table
                        # Ideally `yield for` would be used here, but that is
                        # not python2 compatible
                        for item in process_table(table_obj,
                                                  raw_keys=match.group('columns'),
                                                  raw_values=match.group('values')):
                            yield item


def process_table(table_schema, raw_keys, raw_values):
    columns_names_to_include = [c.from_name for c in table_schema.columns]
    # We want to implicitely include the primary key field
    columns_names_to_include.extend(['ID', 'id'])

    # Ensure all the column names defined actually exist
    column_names = parse_sql_list(raw_keys)
    for column in table_schema.columns:
       if column.from_name not in column_names:
           raise Exception("Unrecognized table name: %s:%s" % (table_schema.from_table,
                                                               column.from_name))

    for counter, item in enumerate(column_names):
        if item in ['id', 'ID']:
            column_obj = ColumnSchema(from_name=item, to_name='pk', index=counter)
            table_schema.columns.append(column_obj)
        else:
            for column in table_schema.columns:
                if item == column.from_name:
                    column.index = counter
                    break

    new_column_names = [column.to_name for column in table_schema.columns]
    sql_column_indices = [column.index for column in table_schema.columns]

    insert_rows = sql_list_splitter(raw_values)
    values_list_of_lists = (parse_sql_list(l, column_filter=sql_column_indices) for l in insert_rows)

    # convert data to dictionary and append to results
    for values_list in values_list_of_lists:
        yield create_fixture_item(keys=new_column_names, values=values_list,
                                  model=table_schema.to_table)
