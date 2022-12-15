from advent_of_code.parsers import parse_lines


def test_parse_lines_no_func():
    test_input = """\
one
two
three
"""

    assert list(parse_lines(input_s=test_input)) == ["one", "two", "three"]


def test_parse_lines_func():
    test_input = """\
1
2
3
"""

    assert list(parse_lines(input_s=test_input, tx_func=int)) == [1, 2, 3]
