from collection import util

class GameSummary():
	def __init__(self):
		self.attendance = None
		self.goals = []
		
	def set_timespan(self, start, end):
		self.start = start
		self.end = end
		self.duration = end - start
	
	def get_goal_table_string(self):
		data = '\n'.join([str(g) for g in self.goals])
		return 'P Time  Tm.  G A1 A2 Away              Home\n' + data
	
	@staticmethod
	def get_penalty_table_string(penalties):
		data = '\n'.join([str(i) for i in penalties])
		return 'P Time  Pl M Type\n' + data
		
	@staticmethod
	def get_period_table_string(periods):
		data = '\n'.join(['{:1} {}'.format(i+1,v) for i,v in enumerate(periods)])
		return 'P  G  S Pn PM\n' + data
	
	def get_star_table_string(self):
		data = '\n'.join(['{:1} {}'.format(i+1,v) for i,v in enumerate(self.stars)])
		return '# Tm  P Pl\n' + data
		
	def __repr__(self):
		format = \
'''{date}
{start}-{end} ({duration})
{attendance} people at {venue}

Goals:
{goals}

Home Penalties:
{home_penalties}
Away Penalties:
{away_penalties}

Home Periods:
{home_periods}
Away Periods:
{away_periods}

Referees:
{referees}
Linesmen:
{linesmen}

Stars:
{stars}'''
		return format.format(
			date=self.start.strftime('%Y-%m-%d'),
			start=self.start.strftime('%H:%M'),
			end=self.end.strftime('%H:%M'),
			duration=self.duration,
			attendance=self.attendance if self.attendance else 0,
			venue=self.venue,
			goals=self.get_goal_table_string(),
			home_penalties=self.get_penalty_table_string(self.home_penalties),
			away_penalties=self.get_penalty_table_string(self.away_penalties),
			home_periods=self.get_period_table_string(self.home_periods),
			away_periods=self.get_period_table_string(self.away_periods),
			referees=util.get_number_list_string(self.referees),
			linesmen=util.get_number_list_string(self.linesmen),
			stars=self.get_star_table_string()
		)
