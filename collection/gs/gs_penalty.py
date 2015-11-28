from collection import util

class Penalty():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{:1} {:>5} {:2} {:1} {:15}'.format(
			self.period,
			self.time,
			util.nz(self.player),
			self.minutes,
			self.penalty_type
		)
		
def get_team_penalties_from_table(table):
	penalties = []
	
	for tr in table('tr', recursive=False)[1:]:
		(number, period, time, player, minutes, penalty_type) = \
			[util.clean_nbsp(td.text).strip() for td in tr('td', recursive=False)]
		
		p = Penalty()
		
		# how will this be recorded in playoffs when multiple OT periods?
		if period == 'OT': period = 4
		p.period = int(period)
		
		p.time = time
		
		try: p.player = util.get_integer(player)
		# Can have whole-team penalties with no player
		except ValueError: p.player = None
		p.minutes = int(minutes)
		p.penalty_type = penalty_type
		
		penalties.append(p)
		
	return penalties
	
def set_penalty_summary(self, soup):
	# find penalty data
	# penalty_summary_table = soup.find(id='PenaltySummary')
	penalty_summary_table = soup.td.table
	data_tr = penalty_summary_table('tr')[1].td.table.tr.td.table.tr
	
	# find penalty table for each team
	away = data_tr.td.table
	home = data_tr('td', recursive=False)[-1].table
	
	self.home_penalties = get_team_penalties_from_table(home)
	self.away_penalties = get_team_penalties_from_table(away)
	