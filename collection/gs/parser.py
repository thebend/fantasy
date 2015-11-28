from bs4 import BeautifulSoup
from game_summary import GameSummary
import gs_gameinfo
import gs_score
import gs_penalty
import gs_period
import gs_official
import gs_star

def parse(html):
	soup = BeautifulSoup(html, 'html.parser')
	gs = GameSummary()
	
	try:
		gs_gameinfo.set_game_info(soup, gs)
	except ValueError:
		# if we didn't get game info, this is an empty report
		return None
	
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
	
	gs_score.set_scoring_summary(gs, scoring_summary)
	gs_penalty.set_penalty_summary(gs, penalty_summary)
	gs_period.set_period_summary(gs, period_summary)
	
	(officials, stars) = officials_stars.td.table('tr', recursive=False)[1]('td', recursive=False)
	gs_official.set_officials(gs, officials)
	gs_star.set_stars(gs, stars)
	
	return gs
		
	