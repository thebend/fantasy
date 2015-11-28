from bs4 import BeautifulSoup
from game_summary import GameSummary
from gs_gameinfo import set_game_info
from gs_score import set_scoring_summary
from gs_penalty import set_penalty_summary
from gs_period import set_period_summary
from gs_official import set_officials
from gs_star import set_stars

def parse(html):
	soup = BeautifulSoup(html, 'html.parser')
	gs = GameSummary()
	
	# identify main table sections
	(
		game_summary,
		p1, h1,
		scoring_summary,
		p2, h2,
		penalty_summary,
		p3,
		period_summary,
		p4,
		power_plays,
		even_strength,
		p5, h5,
		goaltender_summary,
		p6,
		officials_stars,
		p7,
		copyright
	) = soup.find(id='MainTable')('tr', recursive=False)
	
	try:
		set_game_info(gs, game_summary)
	except ValueError:
		# if we didn't get game info, this is an empty report
		return None
	
	set_scoring_summary(gs, scoring_summary)
	set_penalty_summary(gs, penalty_summary)
	set_period_summary(gs, period_summary)
	
	(officials, stars) = officials_stars.td.table('tr', recursive=False)[1]('td', recursive=False)
	set_officials(gs, officials)
	set_stars(gs, stars)
	
	return gs
		
	