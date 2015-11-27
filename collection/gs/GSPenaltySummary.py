import Util

class Penalty():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{:1} {:5} {:2} {:1} {:15}'.format(
			self.period,
			self.time,
			self.player,
			self.minutes,
			self.penalty_type
		)
		
def get_team_penalties_from_table(table):
	penalties = []
	
	for tr in table('tr', recursive=False)[1:]:
		td_text = [Util.clean_nbsp(td.text).strip() for td in tr('td', recursive=False)]
		(number, period, time, player, minutes, penalty_type) = td_text
		# just get player number
		player = player.split(' ')[0].strip()
		
		p = Penalty()
		p.period = int(period)
		p.time = time
		p.player = int(player)
		p.minutes = int(minutes)
		p.penalty_type = penalty_type
		
		penalties.append(p)
		
	return penalties
	
def set_penalty_summary(soup, gs):
	penalty_summary_table = soup.find(id='PenaltySummary')
	data_tr = penalty_summary_table('tr')[1].td.table.tr.td.table.tr
	
	away = data_tr.td.table
	home = data_tr('td', recursive=False)[-1].table
	
	gs.home_penalties = get_team_penalties_from_table(home)
	gs.away_penalties = get_team_penalties_from_table(away)
	