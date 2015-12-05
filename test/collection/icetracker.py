import set_path
from collection import icetracker

# will still have to load list of games to loop through each of them
sample_game_id = '2015020273'
data = icetracker.get_ice_tracker_data(sample_game_id)

for i in data:
	if i.event_type == 'Goal': print str(i)
