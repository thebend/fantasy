import set_path
import sys
import ConfigParser
from collection.nhl_reportdownloader import get_all_game_report_html

config = ConfigParser.RawConfigParser()
config.read('fantasy.conf')
seasons = [int(i) for i in config.get('tests','seasons').split(',')]
gametypes = [int(i) for i in config.get('tests','gametypes').split(',')]
games = config.getint('tests','games')

test = sys.argv[1].upper() # passed in as command line argument

from datetime import datetime
start_time = datetime.now()

# set appropriate parser function
if test == 'GS':
	from collection.gs import GameSummary
	parse = GameSummary.get_from_html
elif test == 'FC':
	from collection import fc
	parse = fc.get_from_html
elif test == 'ES':
	from collection import es
	parse = es.get_from_html
	
# download, parse, and print data
for report_html in get_all_game_report_html(test, seasons, gametypes, games):
	print parse(report_html)

end_time = datetime.now()
execution_time = end_time - start_time
print 'Total execution time: %s' % execution_time