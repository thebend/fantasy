import set_path
import sys
import ConfigParser
from collection import downloader
from collection.nhlreport import urlgenerator

config = ConfigParser.RawConfigParser()
config.read('fantasy.conf')
seasons = [int(i) for i in config.get('tests','seasons').split(',')]
game_types = [int(i) for i in config.get('tests','game_types').split(',')]
games = config.getint('tests','games')

test = sys.argv[1].upper() # passed in as command line argument

from datetime import datetime
start_time = datetime.now()

# set appropriate parser function
if test == 'GS':
	from collection.nhlreport import gs
	parse = gs.GameSummary.get_from_html
elif test == 'FC':
	from collection.nhlreport import fc
	parse = fc.get_from_html
elif test == 'ES':
	from collection.nhlreport import es
	parse = es.get_from_html
	
# download, parse, and print data
urls = urlgenerator.get_game_report_urls(test, seasons, game_types, games)
for (url, html) in downloader.get_all_html(urls):
	# Some tests print results directly, some return string
	# Only print when something returned
	print url
	result = parse(html)
	if result:
		print result

end_time = datetime.now()
execution_time = end_time - start_time
print 'Total execution time: %s' % execution_time