from bs4 import BeautifulSoup
from GameSummary import GameSummary
import GSGameInfo
import GSScoreSummary
import GSPenaltySummary
import GSPeriodSummary
import GSOfficials
import GSStars

def parse(html):
	soup = BeautifulSoup(html, 'html.parser')
	gs = GameSummary()
	
	try:
		GSGameInfo.set_game_info(soup, gs)
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
	
	GSScoreSummary.set_scoring_summary(gs, scoring_summary)
	GSPenaltySummary.set_penalty_summary(gs, penalty_summary)
	GSPeriodSummary.set_period_summary(gs, period_summary)
	
	(officials, stars) = officials_stars.td.table('tr', recursive=False)[1]('td', recursive=False)
	GSOfficials.set_officials(gs, officials)
	GSStars.set_stars(gs, stars)
	
	return gs
		
	