from collection import util

def get_officials_from_table(table):
	return [util.get_integer(tr.text) for tr in table('tr')]
	
def set_officials(self, soup):
	# find cells with referee and linesmen lists
	(referee_td, linesmen_td) = soup.table('tr', recursive=False)[1]('td', recursive=False)
	
	self.referees = get_officials_from_table(referee_td.table)
	self.linesmen = get_officials_from_table(linesmen_td.table)
	