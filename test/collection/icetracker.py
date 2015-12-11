import set_path
from collection import icetracker
from collection import downloader

def get_icetracker_gameids(start_game_id, number_games):
	for i in range(number_games):
		game_id = str(int(start_game_id) + i)
		yield game_id

def get_icetracker_urls(game_ids):
	for i in game_ids:
		yield icetracker.get_url(i)

# need to bind metadata like this game_id to the parser
# so I can associate returned records in pool
# which may return out of order
ids = get_icetracker_gameids('2015020122', 100)
urls = get_icetracker_urls(ids)
for html in downloader.get_all_html(urls):
	data = icetracker.get_data(html)
	for i in data:
		if i.event_type == 'Penalty':
			print str(i)
