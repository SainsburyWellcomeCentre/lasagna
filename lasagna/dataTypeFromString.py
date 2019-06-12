import re

"""
Module to infer data type from string or convert a string to a data type. 

"""



def dataTypeFromString(string):
	"""
	Returns the data type which string appears to be: int, float, or str
	"""
	#if all integers return int
	if re.match('^[0-9]+$',string) != None :
		return int

	#if all integers with on . somewhere return float
	if re.match('^[0-9]+\.[0-9]+$',string) != None :
		return float

	#if there is any non-numeric character return string
	if re.match('.*\D.*',string) != None :
		return str

	return None


def convertString(string):
	"""
	converts string to float or int (or returns a str) based on the pattern of the string
	"""

	dataType = dataTypeFromString(string)
	if dataType is None:
		return string
	else:
		return dataType(string)



if __name__ == '__main__':
	#testing code
	if dataTypeFromString('32423') != int:
		print('failed int test 1')

	if dataTypeFromString('3') != int:
		print('failed int test 2')

	if dataTypeFromString('3.0') != float:
		print('failed float test 1')

	if dataTypeFromString('33342.0234') != float:
		print('failed float test 2')

	if dataTypeFromString('33342F.0234') != str:
		print('failed str test 1')

	if dataTypeFromString('aardvark') != str:
		print('failed str test 2')

	if dataTypeFromString('AardvarK') != str:
		print('failed str test 3')

	if dataTypeFromString('1.2.3') != str:
		print('failed str test 4')


	#try some conversions
	conversions = ['123','1','1.1','1.2.2','hello']
	for c in conversions:
		converted=convertString(c)
		print("converted %s as %s" % (c,str(type(converted))))
