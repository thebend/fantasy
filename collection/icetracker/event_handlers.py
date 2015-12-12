'''
This isn't formatted well.
Some events will go into their own table.
Some will follow a generic format.
Must develop factory to differentiate automatically
'''

class Player():
	def __init__(self, number, name):
		self.number = number
		self.name = name
		
	def __repr__(self):
		return '{}: {}'.format(self.number, self.name)

handler = {}
def icetracker_handler(event_type):
	"""
	Decorator to build a dictionary of
	event types to their description handlers
	"""
	def get_handler(f):
		handler[event_type] = f
		return f
	return get_handler

# we don't need to consider period end an event
@icetracker_handler('Period End')
def period_end_processor(text):
	return None
	
# details only contains the player name
@icetracker_handler('Giveaway')
def giveaway_processor(text):
	return text
	
# details only contains the player name
@icetracker_handler('Takeaway')
def takeaway_processor(text):
	return text
	
# "Foo Hit Bar" format
@icetracker_handler('Hit')
def hit_processor(text):
	return text.split(' hit ')
	
# "Foo won against Bar" format
@icetracker_handler('Faceoff')
def faceoff_processor(text):
	return text.split(' won against ')
	
SHOT_TYPES = {
	'Wrist Shot',
	'Wrap-around',
	'Slap Shot',
	'Snap Shot',
	'Backhand',
	'Slap Shot',
	'Tip-In',
	'Deflected',
	'null'
}
# "Kevin Bieksa Backhand saved by Pekka Rinne" format
@icetracker_handler('Shot')
def shot_processor(text):
	for shot_type in SHOT_TYPES:
		if shot_type in text:
			(shooter, goalie) = text.split(' {} '.format(shot_type))
			goalie = goalie[9:]
			if shot_type == 'null':
				shot_type = None
			return (shot_type, shooter, goalie)
	raise Exception('Could not match a shot type for "{}"'.format(text))
	
@icetracker_handler('Shootout Goal')
def shootout_goal_processor(text):
	return text.split(' - ')
	
@icetracker_handler('Shootout Missed')
def shootout_missed_processor(text):
	return text.split(' - ')
	
@icetracker_handler('Shootout Shot')
def shootout_shot_processor(text):
	return shot_processor(text)
	
PENALTY_TYPES = [
	'Tripping',
	'Closing hand on puck',
	'Hooking',
	'Slashing',
	'Fighting',
	'Roughing',
	'Holding the stick',
	'Unsportsmanlike conduct',
	'Interference - Goalkeeper', # important this gets processed before regular interference!
	'Interference',
	'Hi-sticking',
	'Holding',
	'Delaying Game - Illegal play by goalie',
	'Delaying Game - Puck over glass',
	'Boarding',
	'Cross checking',
	'Delay of game',
	'Illegal check to head',
	'Misconduct',
	'Match penalty',
	'Illegal stick',
	'PS - Slash on breakaway', # Can anything be prefixed with PS - (penalty shot)?
	'Charging',
	'Delay Gm - Face-off Violation',
	'Game misconduct',
	'Elbowing',
	'Clipping',
	'Too many men/ice',
	'Hi stick - double minor', # why is this specifically a double minor?  Can anything be?
	'Embellishment',
	'Checking from behind',
	'Kneeing',
	'Spearing',
	'Instigator',
	'Delaying the game',
	'Concealing puck',
	'Leaving penalty box',
	'Goalie leave crease',
	'PS - Covering puck in crease',
	'Bench', # what kind of penalty is this?
	'Delaying Game - Smothering puck',
	'Throwing stick',
	'Abuse of officials',
	'Face-off violation',
	'Abusive language',
	'Aggressor',
	'Abuse of Officials',
	'Broken stick',
	'PS - Thow object at puck'
]
from collection import util
class Penalty:
	def __repr__(self):
		return '{:20.20} {:20.20} {:20.20} {:20.20}'.format(
			util.nz(self.aggressor).encode('utf8'),
			self.penalty_type,
			util.nz(self.casualty).encode('utf8'),
			util.nz(self.servee).encode('utf8')
		)
@icetracker_handler('Penalty')
def penalty_processor(text):
	p = Penalty()
	p.servee = None
	p.casualty = None
	
	# some strings are corrupted, eg "against Derek StepanFace-off violation"
	# process these separately
	if text.startswith('against '):
		text = text[8:]
		if ' served by ' in text:
			(text, p.servee) = text.split(' served by ')
		for penalty_type in PENALTY_TYPES:
			if penalty_type in text:
				p.penalty_type = penalty_type
				p.aggressor = text[:-len(penalty_type)]
				
	if ' served by ' in text:
		(text, p.servee) = text.split(' served by ')
	if ' against ' in text:
		(text, p.casualty) = text.split(' against ')
		
	for penalty_type in PENALTY_TYPES:
		if penalty_type in text:
			p.penalty_type = penalty_type
			p.aggressor = text[:-len(penalty_type) - 1]
			if len(p.aggressor) == 0:
				p.aggressor = None
			
			return p
	raise Exception('Could not match a penalty type for "{}"'.format(text))
	
@icetracker_handler('Goal')
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
			player_name = text[processed:i-1]
			processed = i
		elif c == ')': # end of player number
			# don't actually think this is the player number?  What is it?
			player_number = int(text[processed+1:i])
			players.append(Player(player_number, player_name))
			processed = i+2
		elif c == ':': # start of assists list
			shot_type = text[processed:i-9]
			processed = i+2
	
	shooter = players[0]
	assists = players[1:]
	return shooter, shot_type, assists
