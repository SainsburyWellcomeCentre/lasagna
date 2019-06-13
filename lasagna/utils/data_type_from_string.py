import re

"""
Module to infer data type from string or convert a string to a data type. 

"""


def data_type_from_string(input_string):
    """
    Returns the data type which string appears to be: int, float, or str
    """
    # if all integers return int
    if re.match('^[0-9]+$', input_string) is not None:
        return int

    # if all integers with on . somewhere return float
    if re.match('^[0-9]+\.[0-9]+$', input_string) is not None:
        return float

    # if there is any non-numeric character return string
    if re.match('.*\D.*', input_string) is not None:
        return str

    return None


def convert_string(input_string):
    """
    converts string to float or int (or returns a str) based on the pattern of the string
    """
    data_type = data_type_from_string(input_string)
    if data_type is None:
        return input_string
    else:
        return data_type(input_string)


if __name__ == '__main__':
    # testing code
    if data_type_from_string('32423') != int:
        print('failed int test 1')

    if data_type_from_string('3') != int:
        print('failed int test 2')

    if data_type_from_string('3.0') != float:
        print('failed float test 1')

    if data_type_from_string('33342.0234') != float:
        print('failed float test 2')

    if data_type_from_string('33342F.0234') != str:
        print('failed str test 1')

    if data_type_from_string('aardvark') != str:
        print('failed str test 2')

    if data_type_from_string('AardvarK') != str:
        print('failed str test 3')

    if data_type_from_string('1.2.3') != str:
        print('failed str test 4')

    # try some conversions
    conversions = ['123', '1', '1.1', '1.2.2', 'hello']
    for c in conversions:
        converted = convert_string(c)
        print("converted %s as %s" % (c, str(type(converted))))
