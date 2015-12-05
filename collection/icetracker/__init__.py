import requests
from bs4 import BeautifulSoup
from collection import util

'''
This isn't formatted well.
Some events will go into their own table.
Some will follow a generic format.
Must develop factory to differentiate automatically
'''
SHOT_TYPES = set([
	'Wrist Shot',
	'Wrap-around',
	'Slap Shot',
	'Snap Shot',
	'Backhand',
	'Slap Shot',
	'Tip-In',
	'Deflected'
])

'''
Read this thread: http://stackoverflow.com/questions/6629876/how-to-make-an-anonymous-function-in-python-without-christening-it
Consider making use of decorators instead of this dictionary method
May make code cleaner, would be good to use decorators for learning purposes
'''
def shot_processor(text):
	for shot_type in SHOT_TYPES:
		if shot_type in text:
			(shooter, goalie) = text.split(' {} '.format(shot_type))
			goalie = goalie[9:]
			return (shot_type, shooter, goalie)
	raise Exception('Could not match a shot type for "{}"'.format(text))
	
def faceoff_processor(text):
	return text.split(' won against ')
	
PENALTY_TYPES = set([
	'Tripping',
	'Closing hand on puck',
	'Hooking',
	'Slashing'
])
def penalty_processor(text):
	if ' against ' in text:
		(text, casualty) = text.split(' against ')
	else:
		casualty = None
	for penalty_type in PENALTY_TYPES:
		if penalty_type in text:
			aggressor = text[:-(len(penalty_type) + 2)]
			return (aggressor, penalty_type, casualty)
	return None
	
def giveaway_processor(text):
	return text
	
def takeaway_processor(text):
	return text
	
def hit_processor(text):
	return text.split(' hit ')
	
def period_end_processor(text):
	return None
	
def goal_processor(text):
	"""
	Parses strings like "Shea Weber (6) Slap Shot, assists: Roman Josi (9), Mike Ribeiro (9)
	"""
	# This function isn't particularly maintainable.
	# Consider using regex or searching for keyword assists: none
	processed = 0
	players = []
	for i,c in enumerate(text):
		if c == '(': # start of player number
			player = text[processed:i-1]
			processed = i
		elif c == ')': # end of player number
			player_number = int(text[processed+1:i])
			players.append((player, player_number))
			processed = i+2
		elif c == ':': # start of assists list
			shot_type = text[processed:i-9]
			processed = i+2
	
	shooter = players[0]
	assists = players[1:]
	return shooter, shot_type, assists
	
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
