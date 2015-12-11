# should probably move this to some sort of utility class
nbsp = unichr(160)
def clean_nbsp(text):
	""" return string with non-breaking spaces (unichr(160)) replaced with regular spaces """
	return text.replace(nbsp, ' ')
	
def clean_str(text):
	"""
	return string with non-breaking spaces (unichr(160)) replaced with regular spaces,
	and whitespace stripped from ends of string
	"""
	return clean_nbsp(text).strip()

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
	period = period[0] # only first character of period matters
	if period == 'O': return 4 # OT (overtime) becomes period 4
	if period == 'S': return 5 # SO (shootout) becomes period 5
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
	
db_connection = None
def get_db_connection():
	"""
	Returns a connection to the database,
	using an existing one if available
	or creating a new one if necessary
	"""
	if db_connection: return db_connection
	import pyodbc
	import ConfigParser
	
	config = ConfigParser.RawConfigParser()
	config.read('fantasy.conf')
	
	connection_string = 'DRIVER={{{}}};SERVER={};PORT={};DATABASE={};UID={};PWD={}'.format(
		config.get('database','driver'),
		config.get('database','host'),
		config.get('database','port'),
		config.get('database','database'),
		config.get('database','username'),
		config.get('database','password')
	)
	
	db_connection = pyodbc.connect(connection_string)
	return db_connection