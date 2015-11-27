# should probably move this to some sort of utility class
nbsp = unichr(160)
def clean_nbsp(text):
	""" return string with non-breaking spaces (unichr(160)) replaced with regular spaces """
	return text.replace(nbsp, ' ')
