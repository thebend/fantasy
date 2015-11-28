from collection import util

class Penalty():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{:1} {:>5} {:2} {:1} {:15}'.format(
			self.period,
			self.time,
			self.player,
			self.minutes,
			self.penalty_type
		)
		
def get_team_penalties_from_table(table):
	penalties = []
	
	for tr in table('tr', recursive=False)[1:]:
		(number, period, time, player, minutes, penalty_type) = \
			[util.clean_nbsp(td.text).strip() for td in tr('td', recursive=False)]
		
		p = Penalty()
		p.period = int(period)
		p.time = time
		
		# problem - can have whole-team penalties!
		print player
		p.player = util.get_integer(player)
		p.minutes = int(minutes)
		p.penalty_type = penalty_type
		
		penalties.append(p)
		
	return penalties
	
def set_penalty_summary(gs, soup):
	# find penalty data
	# penalty_summary_table = soup.find(id='PenaltySummary')
	penalty_summary_table = soup.td.table
	data_tr = penalty_summary_table('tr')[1].td.table.tr.td.table.tr
	
	# find penalty table for each team
	away = data_tr.td.table
	home = data_tr('td', recursive=False)[-1].table
	
	gs.home_penalties = get_team_penalties_from_table(home)
	gs.away_penalties = get_team_penalties_from_table(away)
	