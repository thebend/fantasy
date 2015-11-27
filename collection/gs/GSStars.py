import Util

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
		
def set_stars(gs, soup):
	# find star table
	star_table = soup.table.tr.td.table
	
	stars = []
	for tr in star_table('tr'):
		(rank, team, position, player) = [td.text for td in tr('td')]
		s = Star()
		s.rank = int(rank[0])
		s.team = team
		s.position = s.position = position
		s.player = Util.get_integer(player)
		stars.append(s)
		
	gs.stars = stars
	