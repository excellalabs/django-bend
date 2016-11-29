import re

def sql_list_splitter(sqlstr):
    # parse a string of format (0, 'a', 'blah'),('b', 1, 'parens()')
    # into a list for each parentheses group
    #
    # If not wrapped in parentheses, will split on commas
    # e.g. "0, 'a', 'blah, test', 'parens()'"
    # returns [0, "'a'", "'blah, test'", "'parens()'"]
    new_str = ''
    is_open_group = False
    is_open_string = False
    last_char_was_escape = False

    for c in sqlstr:
        if not last_char_was_escape:
            if c == ',' and not is_open_group and not is_open_string:
                c = '\n'
            elif c == ')' and not is_open_group and not is_open_string:
                raise Exception("unexpected ')' when parsing string `%s`" % sqlstr)
            elif c == ')' and is_open_group and not is_open_string:
                is_open_group = not is_open_group
            elif c == '(' and is_open_group and not is_open_string:
                raise Exception("unexpected '(' when parsing string `%s`" % sqlstr)
            elif c == '(' and not is_open_group and not is_open_string:
                is_open_group = not is_open_group
            elif c == "'":
                is_open_string = not is_open_string

            last_char_was_escape = (c == '\\')
        else:
            last_char_was_escape = False
            
        new_str += c

    result = new_str.split('\n')
    return result


def parse_into_object_type(raw_value):
    # Expects a raw value from a SQL list
    # Examples: `ID`, NULL, 'John', '1', 1, or 1.0
    # Also, raw_value may have a leading whitespace character
    # Identify the best Python object type

    if raw_value == 'NULL':
        return None

    try:
        value = int(raw_value)
    except ValueError:
        try:
            value = float(raw_value)
        except ValueError:
            value = None

    # If the value isn't NULL, then let's parse it
    regex = re.compile(r"^ ?[`'\"](?P<value>.*)[`'\"] ?$")
    result = regex.match(raw_value)
    if result:
        value = result.group('value')
    elif isinstance(value, int) or isinstance(value, float):
        return value
    else:
        raise Exception("Unrecognized value format: %s" % raw_value)

    # Number parsing is problematic, for example strings with leading
    # zeros are not the same once parsed as an integer (0023 -> 23).
    # In this case keep the value as a string
    if len(value) > 1 and value[0] == '0':
        return value

    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            # Probably just a regular string
            return value
    

def parse_sql_list(results, column_filter=None):
    # Take sql style list in string format: "('blah', 'derp', 'herp')"
    # Return python list: ['blah', 'derp', 'herp']

    values = sql_list_splitter(results.strip('()'))

    # Cherry pick select column indices if provided
    if column_filter:
        values = [values[i] for i in column_filter]

    return [parse_into_object_type(v) for v in values]
        

