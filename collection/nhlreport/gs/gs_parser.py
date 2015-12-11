from bs4 import BeautifulSoup
import collection.nhlreport.gs

@staticmethod
def get_from_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	
	gs = collection.nhlreport.gs.GameSummary()
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
		gs.set_game_info(game_summary)
	except ValueError:
		# if we didn't get game info, this is an empty report
		return None
	
	gs.set_scoring_summary(scoring_summary)
	gs.set_penalty_summary(penalty_summary)
	gs.set_period_summary(period_summary)
	
	(officials, stars) = officials_stars.td.table('tr', recursive=False)[1]('td', recursive=False)
	gs.set_officials(officials)
	gs.set_stars(stars)
	
	return gs
		
	