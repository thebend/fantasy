import requests
from bs4 import BeautifulSoup
from collection import util

'''
This isn't formatted well.
Some events will go into their own table.
Some will follow a generic format.
Must develop factory to differentiate automatically
'''
def shot_processor(text):
	return None
	
def faceoff_processor(text):
	return None
	
def penalty_processor(text):
	return None
	
def giveaway_processor(text):
	return None
	
def takeaway_processor(text):
	return None
	
def hit_processor(text):
	return None
	
def period_end_processor(text):
	return None
	
def goal_processor(text):
	return None
	
EVENT_PROCESSORS = {
	'Shot': shot_processor,
	'Faceoff': faceoff_processor,
	'Penalty': penalty_processor,
	'Giveaway': giveaway_processor,
	'Takeaway': takeaway_processor,
	'Hit': hit_processor,
	'Period End': period_end_processor,
	'Goal': goal_processor 
}

class IceTrackerEventDetail():
	def __init__(self, text, event_type):
		self.text = text
		self.event_type = event_type
		self.data = EVENT_PROCESSORS[event_type](text)
		
class IceTrackerRow():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{} {} {:3} {:10} {:55}'.format(
			self.period,
			self.time,
			util.nz(self.team),
			self.event_type,
			self.event_description
		)
		
def get_ice_tracker_data(gameId):
	url = 'http://www.nhl.com/gamecenter/en/icetracker?id=%s' % gameId

	# parse html
	html = requests.get(url).text
	soup = BeautifulSoup(html)

	data = []
	# data in all table rows inside div#allPlays>table
	for tr in soup.find(id='allPlays')('tr'):
		(period, team, eventName, eventDesc, vid) = [util.clean_nbsp(td.text).strip() for td in tr('td')]
		
		r = IceTrackerRow()
		period, time = period.split(' ')
		r.period = util.get_numeric_period(period)
		r.time = time
		
		if len(team) == 0: team = None
		r.team = team

		# period end should really have an event type
		if eventDesc == 'period end': eventName = 'Period End'
		r.event_type = eventName
		r.event_description = eventDesc
		r.details = IceTrackerEventDetail(eventDesc, eventName)

		data.append(r)

	return data
