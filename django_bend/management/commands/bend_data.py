from django.core.management.base import BaseCommand
import os
import re
from django_bend.convert import generate_fixture_tables
from django_bend.schema import TableSchema
import simplejson as json

class Command(BaseCommand):
    help = 'Convert mysqldump to fixtures'

    def add_arguments(self, parser):
        parser.add_argument(
            'input_path', default='.',
            help='Path to the migration definition json files'
        )
        parser.add_argument(
            'mysql_dump',
            help='mysqldump file used as input for translation'
        )
        parser.add_argument(
            '--indent', default=None, dest='indent', type=int,
            help='Specifies the indent level to use when pretty-printing output.',
        )

    def handle(self, *args, **options):
        migration_files = set()
        filename_regex = re.compile(r"^[0-9]{4}_.+.json$")

        input_path = options.get('input_path')
        for name in os.listdir(input_path):
            if filename_regex.match(name):
                migration_files.add(os.path.join(input_path, name))

        tables = []
        for file in migration_files:
            with open(file, 'r') as jsonfile:
                for table in json.load(jsonfile):
                    tables.append(TableSchema.create_from_json(table))

        fixtures = generate_fixture_tables(tableschemas=tables, dumpfilename=options['mysql_dump'])

        print(json.dumps(fixtures, indent=options['indent'], iterable_as_array=True))
