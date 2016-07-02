from django.core.management.base import BaseCommand
import os
from bend.loader import loader
from bend.convert import generate_fixture_tables
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
        for name in os.listdir(options.get('input_path')):
            if name.endswith(".json"):
                migration_files.add("%s/%s" % (options.get('input_path'), name))

        tables = []
        for file in migration_files:
            with open(file, 'r') as jsonfile:
                tables.extend(json.load(jsonfile))

        fixtures = generate_fixture_tables(definition=tables, dumpfilename=options['mysql_dump'])

        print(json.dumps(fixtures, indent=options['indent'], iterable_as_array=True))
