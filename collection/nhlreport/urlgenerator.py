import re
import requests
from collection import util
from datetime import date

GAMETYPE_DESCRIPTION = {
	1: 'Pre-Season',
	2: 'Regular Season',
	3: 'Playoffs'
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

def validate_report_type(report_type):
	if not report_type in REPORT_ABBREVIATION.keys():
		raise ValueError('Invalid report_type (must be one of GS,ES,FC,FS,PL,TV,TH,RO,SS)')

def get_url(season, game_type, game_number, report_type):
	"""
	Return the URL for a particular report type for a particular game
	
	Keyword arguments:
	season -- the int year that the season started in
	game_type -- int 1 (Pre-Season), 2 (Regular Season), 3 (Playoffs) 
	game_number -- int identifying game by number, in sequence for that season and game_type
	report_type -- two character abbreviation for game type. One of GS|ES|FC|FS|PL|TV|TH|RO|SS
	
	returns string like "http://www.nhl.com/scores/htmlreports/20142015/GS010001.HTM"
	"""
	
	if not 1900 <= season <= date.today().year:
		raise ValueError('Season must be a year no greater than the current year')
	if not 1 <= game_type <= 3:
		raise ValueError('Invalid game_type (must be 1, 2, or 3)')
	if not 1 <= game_number <= 9999:
		raise ValueError('Invalid game_number (must be between 1 and 9999)')
		
	url = 'http://www.nhl.com/scores/htmlreports/{}{}/{}{:02d}{:04d}.HTM'.format(
		season, season + 1,
		report_type.upper(), game_type, game_number
	)
	return url
	
GAMELIST_URL_FORMAT = 'http://www.nhl.com/ice/schedulebyseason.htm?season={}{}&gameType={}'
def get_gamelist_url(season, game_type):
	return GAMELIST_URL_FORMAT.format(
		season,
		season + 1,
		game_type
	)
	
gameid_re = re.compile('href="http://www.nhl.com/gamecenter/en/recap\\?id=\\d{6}(\\d{4})"')
def get_game_numbers(html):
	return [int(i) for i in gameid_re.findall(html)]

def get_game_report_urls(report_types, seasons, game_types, category_games = 0, starting_game_number = 0):
	"""
	Yields URLs for all available game reports matching given criteria
	
	Keyword arguments:
	report_types -- list of two-letter string abbreviations
	seaasons -- list of integer years indicating start of target seasons
	game_types -- list of game types, any of 1, 2, or 3
	starting_game_number -- integer for lowest of game numbers to retrieve
	"""
	# some arguments can be given as singular
	# but will treat as 1-item tuples later
	report_types = util.make_iterable(report_types)
	seasons = util.make_iterable(seasons)
	game_types = util.make_iterable(game_types)
	
	for i in report_types:
		validate_report_type(i)
		
	for season in seasons:
		for game_type in game_types:
			print 'Beginning search of {}-{} {} games...'.format(
				season, season+1,
				GAMETYPE_DESCRIPTION[game_type]
			)
			
			gamelist_url = get_gamelist_url(season, game_type)
			response = requests.get(gamelist_url)
			html = response.text
			game_numbers = get_game_numbers(html)
			
			target_game_numbers = sorted([i for i in game_numbers if i >= starting_game_number])
			# limit number of games returned per category if requested
			if category_games > 0:
				target_game_numbers = target_game_numbers[:min(len(target_game_numbers),category_games)]
			for game_number in target_game_numbers:
				for report_type in report_types:
					url = get_url(season, game_type, game_number, report_type)
					yield url
					