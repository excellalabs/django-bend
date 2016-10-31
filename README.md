# Django Bend

[![Build Status](https://travis-ci.org/excellalabs/django-bend.svg?branch=master)](https://travis-ci.org/excellalabs/django-bend)
[![Coverage Status](https://coveralls.io/repos/excellalabs/django-bend/badge.svg?branch=master&service=github)](https://coveralls.io/github/excellalabs/django-bend?branch=master)

A tool to help translate a legacy mysqldump to fixtures for a similar-but-different Django model.

The use case for this tool is when you want to port data from a legacy system, but your Django models were designed in a way that the data doesn't quite align correctly.  Table names and column names could be different, or columns could be completely missing.

See the example below for a Before and After scenario.

### How to install

Note that django-bend requires Django >=1.8.0.  This requirement is not enforced via `pip install` to prevent the scenario of unknowingly upgrading your Django version.

Install django-bend

```shell
pip install django-bend
```

Add bend to your Django INSTALLED_APPS

```python
INSTALLED_APPS = (
    ...
    'django_bend',
)
```

### Create your schema

The example for this readme expects a mysqldump file with the following table:

Filename: sample.sql

```sql
CREATE TABLE `ftbl_individuals` (
  `ID` int(10) NOT NULL,
  `FirstName` varchar(25) DEFAULT NULL,
  `LastName` varchar(30) DEFAULT NULL,
  `Middle` varchar(30) DEFAULT NULL,
  `Gender` varchar(1) DEFAULT NULL,
  `DOB` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Constraint` (`FirstName`,`LastName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `ftbl_individuals` (`ID`, `FirstName`, `LastName`, `Middle`, `Gender`, `DOB`) VALUES ('1','Frank','Thomas','L','M','1972-11-28 00:00:00'),('2','Carlos','Baerga','3','M','1966-05-08 00:00:00'),('3','Dolly','Parton','#','F','2000-02-24 00:00:00');
```

Suppose the Django model looks like this:

Filename: myapp/models.py

```python
class Person(models.Model):
    first_name = models.TextField()
    date_of_birth = models.DateTimeField(blank=True, null=True)
```

Create a mapping json file with a naming convention similar to Django Migrations:

Filename: myapp/bend/0001_person.json

```json
[
  {
    "from_table": "ftbl_individuals",
    "to_table": "foo.person",
    "columns": [
      {
        "from": "FirstName",
        "to": "first_name"
      },
      {
        "from": "DOB",
        "to": "date_of_birth"
      }
    ]
  }
]
```

Your individual columns can have data mapping values for cleaning up bad data:

```json
[
  {
    "from_table": "ftbl_individuals",
    "to_table": "foo.person",
    "columns": [
      {
        "from": "FirstName",
        "to": "first_name"
      },
      {
        "from": "DOB",
        "to": "date_of_birth"
      },
      {
        "from": "Active",
        "to": "is_active",
        "mapping":
        [
            {"to": 1, "from": 2},
            {"to": 0, "from": 1}
        ]
      }
    ]
  }
]
```

You can define more tables in the same file, or create new files for new definitions (e.g. `myapp/bend/0002_company.json`). Bend will find all the files that match the `XXXX_name.json` format where X is a digit.

### Create the fixture file

Run `./manage.py bend_data myapp/bend/ sample.sql --indent=2` to dump the fixture output to the terminal.

```json
[
  {
    "fields": {
      "first_name": "Frank",
      "date_of_birth": "1972-11-28 00:00:00"
    },
    "model": "foo.person",
    "pk": 1
  },
  {
    "fields": {
      "first_name": "Carlos",
      "date_of_birth": "1966-05-08 00:00:00"
    },
    "model": "foo.person",
    "pk": 2
  },
  {
    "fields": {
      "first_name": "Dolly",
      "date_of_birth": "2000-02-24 00:00:00"
    },
    "model": "foo.person",
    "pk": 3
  }
]
```

If it looks like what you expect, pipe it to a fixture file:

```shell
./manage.py bend_data myapp/bend/ sample.sql > myapp/fixtures/bend.json
```

The fixture can then be loaded easily:

```shell
./manage.py loaddata myapp/fixtures/bend.json
```
