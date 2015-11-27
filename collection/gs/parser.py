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
		self.goals = []
		
	def set_timespan(self, start, end):
		self.start = start
		self.end = end
		self.duration = end - start
	
	def get_goal_table_string(self):
		return 'P Time  Tm.  G A1 A2 Visitors          Home\n' + '\n'.join([str(g) for g in self.goals])
	
	def __repr__(self):
		format = \
'''{date}
{start}-{end} ({duration})
{attendance} people at {venue}
Goals:
{goals}'''
		return format.format(
			date=self.start.strftime('%Y-%m-%d'),
			start=self.start.strftime('%H:%M'),
			end=self.end.strftime('%H:%M'),
			duration=self.duration,
			attendance=self.attendance if self.attendance else 0,
			venue=self.venue,
			goals=self.get_goal_table_string()
		)

def get_nhl_datetime(date, time):
	"""
	date -- string of date formatted like "Wednesday, October 8, 2014"
	time -- string of 12-hour time like "7:15 PM"
	"""
	datetime_string = '{} {} PM'.format(date, time)
	return datetime.datetime.strptime(datetime_string, '%A, %B %d, %Y %I:%M %p')

def set_game_info(soup, gs):
	"""
	Sets the following properties in gs:
	startDatetime
	endDatetime
	duration
	venue
	attendance
	timezone
	"""
	(date, venue, time, gameNumber, final) = [tr.text.strip() for tr in soup.find(id='GameInfo')('tr')[3:8]]
	
	# time originally like "Start 7:15 EDT; End 9:55 EDT"
	# note 12-hour time, assume always PM
	try:
		(start, end) = time.split('; ')
	except ValueError:
		# time will only be "Start : TimeZoneAbbr" if game went unplayed
		raise ValueError('Report is empty')
		
	start_time = start[6:-4]
	end_time = end[4:-4]
	
	# timezone is consistent across host venue and not captured here
	# should process timezone and daylight savings changes in analytics, however 
	timeZone = end[-3:]
	
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
	
def get_player_list_from_text(txt):
	""" return int array from text like '13, 20, 21, 31, 55' """
	return [int(i) for i in txt.split(', ')]

def get_team_list(team):
	""" return list of player numbers like '13,20,21,31,55' """
	return ','.join([str(i) for i in team])
	
class Goal():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{:1} {:>5} {:3} {:2} {:2} {:2} {:17} {:17}'.format(
			self.period,
			self.time,
			self.team,
			self.scorer,
			self.assist1,
			self.assist2 if self.assist2 else '',
			get_team_list(self.visitors),
			get_team_list(self.home)
		)
	
def set_scoring_summary(soup, gs):
	# td with text "SCORING SUMMARY"
	title_td = soup.find('td',text='SCORING SUMMARY')
	# parent tr, parent table, parent td, parent tr
	title_parent_tr = title_td.parent.parent.parent.parent
	# next tr, td, table
	scoring_summary_table = title_parent_tr.find_next_sibling('tr').td.table
	# all trs except first, which is a label
	
	for tr in scoring_summary_table('tr')[1:]:
		(goal_number, period, time, strength, team, scorer, assist1, assist2, visitors, home) = [td.text.strip() for td in tr('td')]
		
		g = Goal()
		g.period = period
		g.time = time
		# g.strength can be inferred from home/visitors count
		g.team = team
		# like "13 C.ATKINSON(1)"
		g.scorer = int(scorer.split(' ')[0])
		# why don't I get errors here when null?
		g.assist1 = int(assist1.split(' ')[0])
		try: g.assist2 = int(assist2.split(' ')[0])
		except ValueError: g.assist2 = None
		
		# like "28, 29, 31, 33, 49, 76"
		# no more than 6 people on ice with two digit numbers plus comma separators
		# 6*2 + 5 = 17 = max length
		
		g.visitors = get_player_list_from_text(visitors)
		g.home = get_player_list_from_text(home)
		gs.goals.append(g)

def parse(html):
	soup = BeautifulSoup(html, 'html.parser')
	gs = GameSummary()
	
	try:
		set_game_info(soup, gs)
	except ValueError:
		return None
	
	set_scoring_summary(soup, gs)
	return gs
		
	