import requests
from bs4 import BeautifulSoup

class IceTrackerRow():
	def __init__(self):
		pass

def get_ice_tracker_data(gameId):
	url = 'http://www.nhl.com/gamecenter/en/icetracker?id=%s' % gameId

	#parse html
	html = requests.get(url).text
	soup = BeautifulSoup(html)

	data = []
	#data in all table rows inside div#allPlays>table
	for tr in soup.find(id='allPlays')('tr'):
		(period, team, eventName, eventDesc, vid) = [td.text for td in tr('td')]
		
		#period originally in format "1st 00:00"
		time = period[-5:]
		if period[0] in ('1','2','3'): period = int(period[0])
		else: period = 4 #overtime
		
		if len(team) == 0: team = None

		#period end should really have an event type
		if eventDesc == 'period end': eventName = 'Period End'

		r = IceTrackerRow()
		r.period = period
		r.time = time
		r.team = team
		r.event_type = eventName
		r.event_description = eventDesc

		data.append(r)

	return data

#will still have to load list of games to loop through each of them
sample_game_id = '2015020279'
data = get_ice_tracker_data(sample_game_id)

types = set()
for i in data:
	types.add(i.event_type)
	print '{} {} {:3} {:10} {:55}'.format(
		i.period,
		i.time,
		'' if i.team == None else i.team, #display '' if None
		i.event_type,
		i.event_description
	)

print types
