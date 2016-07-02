def loader(directory):
    migration_files = set()
    for name in os.listdir(directory):
        if name.endswith(".json"):
            migration_files.add(import_name)

    tables = []
    for file in migration_files:
        with open(file, 'r') as jsonfile:
            tables.extend(json.load(jsonfile))

    return tables

