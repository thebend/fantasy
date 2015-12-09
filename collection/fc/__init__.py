"""
Faceoff Comparison
"""
from collection import util
from bs4 import BeautifulSoup

def get_faceoff_data(text):
	text = util.clean_str(text)
	if len(text) == 0:
		return [0,0]
	
	totals = text.split(' ')[0]
	return [int(i) for i in totals.split('-')[0:2]]

def process_rows(rows):
	for tr in rows:
		td = tr('td', recursive=False)
		if len(tr('td')) == 1:
			# spacer row - switching players
			continue
		if td[0].get('colspan') == '2':
			# details for opponent
			opponent_number = util.get_integer(td[1].text)
			offense = get_faceoff_data(td[2].text)
			defense = get_faceoff_data(td[3].text)
			neutral = get_faceoff_data(td[4].text)
			print opponent_number, offense, defense, neutral
		else:
			# new player
			print td[0].text, td[2].text
		
def get_from_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	rows = soup.table('tr', recursive=False)
	away_rows = rows[2].table('tr', recursive=False)[2:]
	home_rows = rows[4].table('tr', recursive=False)[2:]
	
	print "Home Team"
	process_rows(home_rows)
	print "Away Team"
	process_rows(away_rows)
			
import requests
url = 'http://www.nhl.com/scores/htmlreports/20142015/FC010001.HTM'
response = requests.get(url)
get_from_html(response.text)