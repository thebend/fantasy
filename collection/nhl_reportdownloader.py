import re
import requests
import nhl_urlgenerator

def get_game_report_html(url):
	response = requests.get(url)
	
	# if page not found, we tried loading a game that wasn't reported
	if response.status_code == 404:
		return None
	else:
		return response.text

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

def get_all_game_report_html(
	report_types = ('GS',),
	seasons = (2014,),
	game_types = (2,),
	starting_game_number = 0
):
	"""
	Yield HTML of all specified reports
	
	Keyword arguments:
	report_types -- list of two-letter string abbreviations
	seaasons -- list of integer years indicating start of target seasons
	game_types -- list of game types, any of 1, 2, or 3
	starting_game_number -- integer for lowest of game numbers to retrieve
	"""
	if type(report_types) == str:
		report_types = (report_types,)
	for i in report_types:
		if not i in nhl_urlgenerator.REPORT_ABBREVIATION:
			raise Exception('report_types must be one of GS,ES,FC,FS,PL,TV,TH,RO,SS')
	
	for season in seasons:
		print 'Beginning search of %s-%s season' % (season, season + 1)
		for game_type in game_types:
			print 'Beginning search of %s games...' % (nhl_urlgenerator.GAMETYPE_DESCRIPTION[game_type],)
			
			gamelist_url = get_gamelist_url(season, game_type)
			print gamelist_url
			response = requests.get(gamelist_url)
			html = response.text
			game_numbers = get_game_numbers(html)
			
			target_game_numbers = sorted([i for i in game_numbers if i >= starting_game_number])
			for game_number in target_game_numbers:
				for report_type in report_types:
					url = nhl_urlgenerator.get_game_report_url(season, game_type, game_number, report_type)
					print url
					html = get_game_report_html(url)
					if html:
						yield html
