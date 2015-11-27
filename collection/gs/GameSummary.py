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
		return 'P Time  Tm.  G A1 A2 Visitors          Home\n' + data
	
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
