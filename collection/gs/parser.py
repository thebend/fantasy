from bs4 import BeautifulSoup
import datetime

# should probably move this to some sort of utility class
nbsp = unichr(160)
def clean_nbsp(text):
	""" return string with non-breaking spaces (unichr(160)) replaced with regular spaces """
	return text.replace(nbsp, ' ')

class GameSummary():
	def __init__(self):
		self.attendance = None
		pass
		
	def set_timespan(self, start, end):
		self.start = start
		self.end = end
		self.duration = end - start
	
	def __str__(self):
		return '{date}\n{start}-{end} ({duration})\n{attendance} people at {venue}'.format(
			date=self.start.strftime('%Y-%m-%d'),
			start=self.start.strftime('%H:%M'),
			end=self.end.strftime('%H:%M'),
			duration=self.duration,
			attendance=self.attendance if self.attendance else 0,
			venue=self.venue
		)

def get_nhl_datetime(date, time):
	"""
	date -- string of date formatted like "Wednesday, October 8, 2014"
	time -- string of 12-hour time like "7:15 PM"
	"""
	datetime_string = '{} {} PM'.format(date, time)
	return datetime.datetime.strptime(datetime_string, '%A, %B %d, %Y %I:%M %p')

def parse(html):
	"""
	Returns a complex object containing:
	startDatetime
	endDatetime
	duration
	venue
	attendance
	timezone
	"""
	soup = BeautifulSoup(html, 'html.parser')
	
	(date, venue, time, gameNumber, final) = [tr.text.strip() for tr in soup.find(id='GameInfo')('tr')[3:8]]
	
	# time originally like "Start 7:15 EDT; End 9:55 EDT"
	# note 12-hour time, assume always PM
	try:
		(start, end) = time.split('; ')
	except ValueError:
		# time will only be "Start : TimeZoneAbbr" if game went unplayed
		return None
	start_time = start[6:-4]
	end_time = end[4:-4]
	
	# timezone is consistent across host venue and not captured here
	# should process timezone and daylight savings changes in analytics, however 
	timeZone = end[-3:]
	
	gs = GameSummary()
	gs.set_timespan(
		get_nhl_datetime(date, start_time),
		get_nhl_datetime(date, end_time)
	)
	
	# venue originally like "Attendance 19,745 at Air Canada Centre"
	venue = clean_nbsp(venue).split(' ')
	
	# attendance not always available
	if len(venue[1]) > 0:
		gs.attendance = int(venue[1].replace(',',''))
	
	gs.venue = ' '.join(venue[3:])
	
	return gs
