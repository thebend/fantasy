from bs4 import BeautifulSoup
#from dateutil.parser import parse
import datetime
import re 

nbsp = unichr(160)

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

def getNhlDatetime(date, time):
	"""
	date -- string of date formatted like "Wednesday, October 8, 2014"
	time -- string of 12-hour time like "7:15 PM"
	zone -- timezone like EDT
	"""
	datetimeString = '{} {}'.format(date, time)
	return datetime.datetime.strptime(datetimeString, '%A, %B %d, %Y %I:%M %p')

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
	startTime = start[6:-4] + ' PM'
	endTime = end[4:-4] + ' PM'
	
	# timezone is consistent across host venue and not captured here
	# should process timezone and daylight savings changes in analytics, however 
	timeZone = end[-3:]
	
	gs = GameSummary()
	gs.set_timespan(
		getNhlDatetime(date, startTime),
		getNhlDatetime(date, endTime)
	)
	
	# Attendance 19,745 at Air Canada Centre
	# Replace nbsp with regular space first!
	venue = venue.replace(nbsp,' ').split(' ')
	try:
		gs.attendance = int(venue[1].replace(',',''))
	except ValueError:
		# attendance not always available
		pass
	gs.venue = ' '.join(venue[3:])
	
	return gs

# sampleUrl = 'http://www.nhl.com/scores/htmlreports/20142015/GS010001.HTM'
#html = open('sample.html','r').read()
#print parse(html)