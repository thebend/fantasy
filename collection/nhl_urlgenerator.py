from datetime import date

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
	
	returns string like "http://www.nhl.com/scores/htmlreports/20142015/GS010001.HTM"
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
	