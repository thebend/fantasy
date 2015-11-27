from bs4 import BeautifulSoup
from GameSummary import GameSummary
import GSGameInfo
import GSScoreSummary

def parse(html):
	soup = BeautifulSoup(html, 'html.parser')
	gs = GameSummary()
	
	try:
		GSGameInfo.set_game_info(soup, gs)
	except ValueError:
		# if we didn't get game info, this is an empty report
		return None
	
	GSScoreSummary.set_scoring_summary(soup, gs)
	return gs
		
	