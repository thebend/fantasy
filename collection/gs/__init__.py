from collection import util
	
class GameSummary():
	from gs_parser import get_from_html
	from gs_gameinfo import set_game_info
	from gs_score import set_scoring_summary
	from gs_penalty import set_penalty_summary
	from gs_period import set_period_summary
	from gs_official import set_officials
	from gs_star import set_stars
	
	def __init__(self):
		self.attendance = None
		self.goals = []
		
	def set_timespan(self, start, end):
		self.start = start
		self.end = end
		self.duration = end - start
		
	def get_goal_table_string(self):
		return util.get_table_string('P Time  Tm.  G A1 A2 Away              Home', self.goals)
	
	@staticmethod
	def get_penalty_table_string(penalties):
		return util.get_table_string('P Time  Pl M Type', penalties)
		
	@staticmethod
	def get_period_table_string(periods):
		return util.get_table_string('P  G  S Pn PM', periods)
	
	def get_star_table_string(self):
		return util.get_table_string('# Tm  P Pl', self.stars)
		
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
