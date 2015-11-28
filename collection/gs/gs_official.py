from collection import util

def get_officials_from_table(table):
	return [util.get_integer(tr.text) for tr in table('tr')]
	
def set_officials(gs, soup):
	# find cells with referee and linesmen lists
	(referee_td, linesmen_td) = soup.table('tr', recursive=False)[1]('td', recursive=False)
	
	gs.referees = get_officials_from_table(referee_td.table)
	gs.linesmen = get_officials_from_table(linesmen_td.table)
	