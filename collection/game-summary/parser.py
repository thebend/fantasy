import requests
from bs4 import BeautifulSoup

gameTypes = {
	'1': 'Pre-Season',
	'2': 'Regular Season',
	'3': 'Playoffs'
}

reportAbbreviations = {
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

#must loop through each season
season = 2014
seasonName = '%s%s' % (season, season+1) #eg. 20142015
seasonGameNumber = 0
#only break when an invalid game has been found
for gameType, gameTypeDesc in gameTypes.iteritems():
	gameType = '{:02d}'.format(int(gameType))
	print 'Beginning search of %s games...' % (gameTypeDesc,)
	
	while True:
		seasonGameNumber += 1
		gameId = '{:04d}'.format(seasonGameNumber)
		for reportTypeAbbr,reportType in reportAbbreviations.iteritems():
			#why the 02 portion? before gameid 01 does lead to a real game!
			url = 'http://www.nhl.com/scores/htmlreports/%s/%s%s%s.HTM' % (seasonName, reportTypeAbbr, gameType, gameId)
			if reportTypeAbbr == 'GS':
				print url
				html = requests.get(url).text
				soup = BeautifulSoup(html, 'html.parser')
				(date, venue, time, gameNumber, final) = [tr.text.strip() for tr in soup.find(id='GameInfo')('tr')[3:8]]

				print date  # Wednesday, October 8, 2014
				print time  # Start 7:15 EDT; End 9:55 EDT
				print venue # Attendance 19,745 at Air Canada Centre
