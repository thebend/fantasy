import Util

class Period():
	def __init__(self):
		pass
		
	def __repr__(self):
		return '{:2} {:2} {:2} {:2}'.format(
			self.goals,
			self.shots,
			self.penalties,
			self.penalty_minutes
		)
		
def get_team_periods_from_table(table):
	periods = []
	
	# skip heading row, total row
	for tr in table('tr')[1:-1]:
		td_values = [int(Util.clean_nbsp(td.text).strip()) for td in tr('td')]
		(period, goals, shots, penalties, penalty_minutes) = td_values
		
		p = Period()
		p.goals = goals
		p.shots = shots
		p.penalties = penalties
		p.penalty_minutes = penalty_minutes
		periods.append(p)
		
	return periods
	
def set_period_summary(gs, soup):
	# find penalty data
	# penalty_summary_table = soup.find('td', text='BY PERIOD').parent.parent
	penalty_summary_table = soup.td.table
	penalty_tables_tr = penalty_summary_table('tr')[1].table.tr
	
	# find penalty table for each team
	away_table = penalty_tables_tr.td.table
	home_table = penalty_tables_tr('td', recursive=False)[-1].table
	
	gs.home_periods = get_team_periods_from_table(home_table)
	gs.away_periods = get_team_periods_from_table(away_table)
	