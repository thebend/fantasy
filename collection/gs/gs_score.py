from collection import util

class Goal():
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
			util.nz(self.assist1),
			util.nz(self.assist2),
			util.get_number_list_string(self.away),
			util.get_number_list_string(self.home)
		)
		
def get_number_list_from_text(text):
	""" return int array from text like '13, 20, 21, 31, 55' """
	return [int(i) for i in text.split(', ')]

def set_scoring_summary(gs, soup):
	# find scoring data
	# title_td = soup.find('td',text='SCORING SUMMARY')
	# title_parent_tr = title_td.parent.parent.parent.parent
	# scoring_summary_table = title_parent_tr.find_next_sibling('tr').td.table
	scoring_summary_table = soup.td.table
	
	# all trs except first, which is a label
	for tr in scoring_summary_table('tr')[1:]:
		shot_tds = [td.text.strip() for td in tr('td')]
		# unsuccessful penalty shot
		if shot_tds[0] == '-': continue
		
		(goal_number, period, time, strength, team, scorer) = shot_tds[:6]
		# number of cells is reduced when "Penalty Shot" spans both assist tds
		if shot_tds[6] == 'Penalty Shot':
			assist1 = ''
			assist2 = ''
			(away, home) = shot_tds[-2:]
		else:
			(assist1, assist2, away, home) = shot_tds[-4:]
			
		if period == 'OT': period = '4'
		
		g = Goal()
		g.period = period
		g.time = time
		# g.strength can be inferred from home/away count
		g.team = team
		# like "13 C.ATKINSON(1)"
		g.scorer = int(scorer.split(' ')[0])
		try:
			g.assist1 = int(assist1.split(' ')[0])
			g.assist2 = int(assist2.split(' ')[0])
		except ValueError:
			# it's normal that sometimes we won't have assists		
			pass
			
		try:
			g.away = get_number_list_from_text(away)
			g.home = get_number_list_from_text(home)
			gs.goals.append(g)
		except ValueError:
			# shootouts only list the winning shot?
			# want more data, hopefully elsewhere
			pass
