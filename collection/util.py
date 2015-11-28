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
