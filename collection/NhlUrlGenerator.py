from datetime import date
import requests
from gs.parser import parse

GAMETYPE_DESCRIPTION = {
	'1': 'Pre-Season',
	'2': 'Regular Season',
	'3': 'Playoffs'
}

REPORT_ABBREVIATION = {
	'GS': 'Game Summary',
	'ES': 'Event Summary',
	'FC': 'Faceoff Comparison Report',
	'FS': 'Faceoff Summary Report',
	'PL': 'Full Play-by-Play',
	'TV': 'Time on Ice - Visitors',
	'TH': 'Time on Ice - Home',
	'RO': 'Roster Report',
	'SS': 'Shot Report'
}

def get_game_report_url(season, game_type, game_number, report_type):
	"""
	Return the URL for a particular report type for a particular game
	
	Keyword arguments:
	season -- the int year that the season started in
	game_type -- int 1 (Pre-Season), 2 (Regular Season), 3 (Playoffs) 
	game_number -- int identifying game by number, in sequence for that season and game_type
	report_type -- two character abbreviation for game type. One of GS|ES|FC|FS|PL|TV|TH|RO|SS
	"""
	
	if not 1900 <= int(season) <= date.today().year:
		raise Exception('Season must be a year no greater than the current year')
	if not 1 <= int(game_type) <= 3:
		raise Exception('Invalid game_type (must be 1, 2, or 3)')
	if not 1 <= int(game_number) <= 9999:
		raise Exception('Invalid game_number (must be between 1 and 9999)')
	if not report_type in REPORT_ABBREVIATION.keys():
		raise Exception('Invalid report_type (must be one of GS,ES,FC,FS,PL,TV,TH,RO,SS)')
		
	url = 'http://www.nhl.com/scores/htmlreports/{}{}/{}{:02d}{:04d}.HTM'.format(
		season, int(season) + 1,
		report_type.upper(), int(game_type), int(game_number)
	)
	return url
	
# must loop through each season
season = 2014
# only break when an invalid game has been found
for game_type in ('1','2','3'):
	print 'Beginning search of %s games...' % (GAMETYPE_DESCRIPTION[game_type],)
	game_number = 0
	unreported_games = 0
	while unreported_games < 10:
		game_number += 1
		for report_type in REPORT_ABBREVIATION.keys():
			url = get_game_report_url(season, game_type, game_number, report_type)
			if report_type == 'GS':
				print game_number
				response = requests.get(url)
				
				# if page not found, we tried loading a game that wasn't reported
				# if this has happened 10 times in a row, assume finished and
				# stop processing this series of games
				if response.status_code == 404:
					unreported_games += 1
					break
				else:
					unreported_games = 0
			
				html = response.text
				print parse(html)
