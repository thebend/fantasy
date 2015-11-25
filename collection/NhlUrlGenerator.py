from datetime import date
import requests
from gs.parser import parse

gamesTypeDescription = {
	'1': 'Pre-Season',
	'2': 'Regular Season',
	'3': 'Playoffs'
}

reportAbbreviation = {
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

def getGameReportUrl(season, gameType, gameNumber, reportTypeAbbr):
	"""
	Return the URL for a particular report type for a particular game
	
	Keyword arguments:
	season -- the int year that the season started in
	gameType -- int 1 (Pre-Season), 2 (Regular Season), 3 (Playoffs) 
	gameNumber -- int identifying game by number, in sequence for that season and gameType
	reportTypeAbbr -- two character abbreviation for game type. One of GS|ES|FC|FS|PL|TV|TH|RO|SS
	"""
	
	if not 1900 <= int(season) <= date.today().year:
		raise Exception('Season must be a year no greater than the current year')
	if not 1 <= int(gameType) <= 3:
		raise Exception('Invalid gameType (must be 1, 2, or 3)')
	if not 1 <= int(gameNumber) <= 9999:
		raise Exception('Invalid game number (must be between 1 and 9999)')
	if not reportTypeAbbr in reportAbbreviation.keys():
		raise Exception('Invalid game type (must be one of GS,ES,FC,FS,PL,TV,TH,RO,SS)')
		
	url = 'http://www.nhl.com/scores/htmlreports/{}{}/{}{:02d}{:04d}.HTM'.format(
		season, int(season) + 1,
		reportTypeAbbr.upper(), int(gameType), int(gameNumber)
	)
	return url
	
# must loop through each season
season = 2014
# only break when an invalid game has been found
for gameType in ('1','2','3'):
	print 'Beginning search of %s games...' % (gamesTypeDescription[gameType],)
	gameNumber = 0
	lastGame = False
	unreportedGames = 0
	while unreportedGames < 10:
		gameNumber += 1
		for reportTypeAbbr, reportType in reportAbbreviation.iteritems():
			url = getGameReportUrl(season, gameType, gameNumber, reportTypeAbbr)
			if reportTypeAbbr == 'GS':
				print gameNumber
				response = requests.get(url)
				
				# if page not found, we tried loading a game that wasn't reported
				# if this has happened 10 times in a row, assume finished and
				# stop processing this series of games
				if response.status_code == 404:
					unreportedGames += 1
					break
				else:
					unreportedGames = 0
			
				html = response.text
				print parse(html)
