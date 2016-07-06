from django_bend.parsing import parse_sql_list, parse_into_object_type, sql_list_splitter
import pytest

class TestParseSqlList:

    default_response = ['cat', 'dog', 'fish']

    def test_default_params(self):
        assert parse_sql_list("('cat','dog','fish')") == self.default_response

    def test_no_parentheses(self):
        assert parse_sql_list("'cat','dog','fish'") == self.default_response

    def test_spaces(self):
        assert parse_sql_list("( 'cat', 'dog', 'fish' )") == self.default_response
        assert parse_sql_list("('cat', 'dog', 'fish')") == self.default_response

    def test_column_filter(self):
        assert parse_sql_list("('cat','dog','fish')", column_filter=[1]) == ['dog']
        assert parse_sql_list("('cat','dog','fish')", column_filter=[0,2]) == ['cat', 'fish']

class TestParseIntoObjectType:

    def test_string(self):
        assert parse_into_object_type("`tester_string`") == 'tester_string'
        assert parse_into_object_type('"tester_string"') == 'tester_string'
        assert parse_into_object_type("'tester_string'") == 'tester_string'

    def test_null(self):
        assert parse_into_object_type("NULL") == None

    def test_int(self):
        assert parse_into_object_type("'100'") == 100

    def test_float(self):
        assert parse_into_object_type("'100.0'") == 100.0

    def test_timestamp(self):
        assert parse_into_object_type("'1966-05-08 00:00:00'") == '1966-05-08 00:00:00'

    def test_bad_strings(self):
        with pytest.raises(Exception):
            parse_into_object_type('100')
            parse_into_object_type('tester_string')
        assert parse_into_object_type("'NULL'") == 'NULL'

    def test_phone_numbers(self):
        #TODO this is annoyingly inconsistent
        assert parse_into_object_type("'1234567890'") == 1234567890
        assert parse_into_object_type("'0987654321'") == '0987654321'
        assert parse_into_object_type("'(098)765-4321'") == '(098)765-4321'

class TestSqlListSplitter:

    def test_simple_case(self):
        teststr1 = "(0, 'a', 'dog')"
        teststr2 = "('b', 1, 'cat')"
        assert sql_list_splitter("%s,%s" % (teststr1, teststr2)) == [teststr1, teststr2]

    def test_params(self):
        teststr1 = "(0, '(a', 'dog')"
        teststr2 = "('b', 1, ')cat(')"
        assert sql_list_splitter("%s,%s" % (teststr1, teststr2)) == [teststr1, teststr2]

    def test_quotes(self):
        teststr1 = "(0, '\\'a', 'dog')"
        teststr2 = "('b', 1, 'c\\'at')"
        assert sql_list_splitter("%s,%s" % (teststr1, teststr2)) == [teststr1, teststr2]

    def test_escapes(self):
        teststr1 = "(0, '\\na', 'dog')"
        teststr2 = "('b', 1, '\\'cat')"
        assert sql_list_splitter("%s,%s" % (teststr1, teststr2)) == [teststr1, teststr2]
