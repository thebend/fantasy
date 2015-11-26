import requests
import NhlUrlGenerator

def get_all_game_report_html(report_type):
	if not report_type in NhlUrlGenerator.REPORT_ABBREVIATION:
		raise Exception('report_type must be one of GS,ES,FC,FS,PL,TV,TH,RO,SS')
	
	# must loop through each season
	season = 2014
	for game_type in ('1','2','3'):
		print 'Beginning search of %s games...' % (NhlUrlGenerator.GAMETYPE_DESCRIPTION[game_type],)
		game_number = 0
		unreported_games = 0
		while unreported_games < 10:
			game_number += 1
			url = NhlUrlGenerator.get_game_report_url(season, game_type, game_number, report_type)
			response = requests.get(url)
			
			# if page not found, we tried loading a game that wasn't reported
			# if this has happened 10 times in a row, assume finished and
			# stop processing this series of games
			if response.status_code == 404:
				unreported_games += 1
			else:
				unreported_games = 0
				yield response.text