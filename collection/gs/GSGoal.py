import Util

class GSGoal():
	def __init__(self):
		self.assist1 = None
		self.assist2 = None
		
	def __repr__(self):
		# no more than 6 people on ice with two digit numbers plus comma separators
		# 6*2 + 5 = 17 = max length
		return '{:1} {:>5} {:3} {:2} {:2} {:2} {:17} {:17}'.format(
			self.period,
			self.time,
			self.team,
			self.scorer,
			self.assist1,
			self.assist2 if self.assist2 else '',
			Util.get_number_list_string(self.away),
			Util.get_number_list_string(self.home)
		)
		