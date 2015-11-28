from collection import util

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
		(goals, shots, penalties, penalty_minutes) = \
			[int(util.clean_nbsp(td.text).strip()) for td in tr('td')[1:]]
		
		p = Period()
		# period will be inferred by order
		p.goals = goals
		p.shots = shots
		p.penalties = penalties
		p.penalty_minutes = penalty_minutes
		periods.append(p)
		
	return periods
	
def set_period_summary(self, soup):
	# find penalty data
	# penalty_summary_table = soup.find('td', text='BY PERIOD').parent.parent
	penalty_summary_table = soup.td.table
	penalty_tables_tr = penalty_summary_table('tr')[1].table.tr
	
	# find penalty table for each team
	away_table = penalty_tables_tr.td.table
	home_table = penalty_tables_tr('td', recursive=False)[-1].table
	
	self.home_periods = get_team_periods_from_table(home_table)
	self.away_periods = get_team_periods_from_table(away_table)
	