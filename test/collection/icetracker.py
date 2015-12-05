import set_path
from collection import icetracker

# will still have to load list of games to loop through each of them
sample_game_id = '2015020001'
for i in range(100):
	game_id = str(int(sample_game_id)+i)
	print game_id
	data = icetracker.get_ice_tracker_data(game_id)
	
	for i in data:
		if i.event_type == 'Penalty': print str(i)
