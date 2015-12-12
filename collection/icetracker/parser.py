import requests
from bs4 import BeautifulSoup
from collection import util
import event_handlers

class IceTrackerRow():
	def __repr__(self):
		'''return '{} {} {:3} {:10} {:55}\n{}'.format(
			self.period,
			self.time,
			util.nz(self.team),
			self.event_type,
			self.event_description,
			self.details
		)'''
		return '{}\n{}'.format(
			self.event_description.encode('utf8'),
			self.details
		)
		
ICETRACKER_URL_FORMAT = 'http://www.nhl.com/gamecenter/en/icetracker?id={}'
def get_url(game_id):
	url = ICETRACKER_URL_FORMAT.format(game_id)
	return url
	
def get_data(html):
	soup = BeautifulSoup(html, 'html.parser')

	data = []
	# data in all table rows inside div#allPlays>table
	for tr in soup.find(id='allPlays')('tr'):
		(period, team, eventName, eventDesc, vid) = [util.clean_str(td.text) for td in tr('td')]
		
		r = IceTrackerRow()
		if period == 'Shootout':
			r.period = 5
			r.time = None
			eventName = 'Shootout ' + eventName
		else:
			period, time = period.split(' ')
			r.period = util.get_numeric_period(period)
			r.time = time
		
		if len(team) == 0: team = None
		r.team = team

		# period end should really have an event type
		if eventDesc in ('shootout complete', 'period end'): eventName = 'Period End'
		r.event_type = eventName
		r.event_description = eventDesc
		r.details = event_handlers.handler[eventName](eventDesc)

		data.append(r)

	return data
