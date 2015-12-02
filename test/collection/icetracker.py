import set_path
from collection import icetracker

# will still have to load list of games to loop through each of them
sample_game_id = '2015020279'
data = icetracker.get_ice_tracker_data(sample_game_id)

types = set()
for i in data:
	types.add(str(i.event_type))
	print str(i)

print 'Types:'
print ','.join(types)
