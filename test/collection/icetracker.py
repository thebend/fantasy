import set_path
from collection.icetracker import parser
from collection import downloader
from collection import util

def get_icetracker_gameids(start_game_id, number_games):
	for i in range(number_games):
		game_id = str(int(start_game_id) + i)
		yield game_id

def get_icetracker_urls(game_ids):
	for i in game_ids:
		yield parser.get_url(i)

ids = get_icetracker_gameids('2014021045', 500)
urls = get_icetracker_urls(ids)
for (url, html) in downloader.get_all_html(urls):
	print url
	data = parser.get_data(html)
	for i in data:
		if i.event_type == 'Penalty':
			print str(i)

def test_penalty_parser():
	test_data = [
		'Brandon Sutter Interference - Goalkeeper against Sergei Bobrovsky',
		'Adam Larsson Interference against Jared McCann served by Bobby Farnham',
		'Leaving penalty box',
		' against Tanner GlassAbusive language served by Mike Hoffman'
		' against Hampus LindholmPlayer leaves bench'
		' against Derek StepanFace-off violation'
	]
	
	from collection.icetracker.event_handlers import penalty_processor
	for i in test_data:
		print i
		print penalty_processor(i)
		
# test_penalty_parser()
