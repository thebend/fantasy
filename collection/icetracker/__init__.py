import requests
from bs4 import BeautifulSoup
from collection import util
import icetracker_event_handlers

class IceTrackerEventDetail():
	def __init__(self, text, event_type):
		self.text = text
		self.event_type = event_type
		self.data = icetracker_event_handlers.handler[event_type](text)
		
	def __repr__(self):
		return str(self.data)
		
class IceTrackerRow():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{} {} {:3} {:10} {:55}\n{}'.format(
			self.period,
			self.time,
			util.nz(self.team),
			self.event_type,
			self.event_description,
			self.details
		)
		
def get_ice_tracker_data(gameId):
	url = 'http://www.nhl.com/gamecenter/en/icetracker?id=%s' % gameId

	# parse html
	html = requests.get(url).text
	soup = BeautifulSoup(html, 'html.parser')

	data = []
	# data in all table rows inside div#allPlays>table
	for tr in soup.find(id='allPlays')('tr'):
		(period, team, eventName, eventDesc, vid) = [str(util.clean_nbsp(td.text).strip()) for td in tr('td')]
		
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
