# should probably move this to some sort of utility class
nbsp = unichr(160)
def clean_nbsp(text):
	""" return string with non-breaking spaces (unichr(160)) replaced with regular spaces """
	return text.replace(nbsp, ' ')

def get_integer(text):
	"""
	return integer of all digits in text combined,
	eg "$123,456.08" returns int 12345608
	"""
	return int(''.join(c for c in text if c.isdigit()))

def get_number_list_string(numbers):
	""" return list of player numbers like '13,20,21,31,55' """
	return ','.join([str(i) for i in numbers])

def nz(data, default=''):
	return data if data else default
	
def get_number_list_from_text(text):
	""" return int array from text like '13, 20, 21, 31, 55' """
	return [int(i) for i in text.split(', ')]
	
def get_numeric_period(period):
	""" returns the period as an integer, converting OT to 4 if necessary """
	if period == 'OT': return 4
	# in playoff games, OT periods are numbered 4, 5, 6... automatically
	return int(period)
	
def get_table_string(heading, data):
	"""
	Converts each data element to a string,
	separated by a newline and prefixed with the given heading
	
	Keyword arguments:
	heading -- a typically one-line string to label data
	data -- iterable collection of data
	"""
	data_string = '\n'.join([str(i) for i in data])
	return heading+'\n'+data_string
	