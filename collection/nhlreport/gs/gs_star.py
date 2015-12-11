from collection import util

class Star():
	def __init__(self):
		pass
	
	def __repr__(self):
		return '{:1} {:3} {:1} {:>2}'.format(
			self.rank,
			self.team,
			self.position,
			self.player
		)
		
def set_stars(self, soup):
	star_table = soup.table.table
	
	stars = []
	for tr in star_table('tr'):
		(rank, team, position, player) = [td.text for td in tr('td')]
		# sometimes no stars given, which causes blank team
		if len(team) == 0: break
		
		s = Star()
		# rank can be inferred by order in list
		s.rank = int(rank[0])
		s.team = team
		s.position = position
		s.player = util.get_integer(player)
		stars.append(s)
		
	self.stars = stars
	