import Util

def get_officials_from_table(table):
	return [Util.clean_nbsp(tr.text).strip() for tr in table('tr')]
	
def set_officials(gs, soup):
	# find cells with referee and linesmen lists
	(referee_td, linesmen_td) = soup.td.table('tr', recursive=False)[1]('td', recursive=False)
	
	gs.referees = get_officials_from_table(referee_td.table)
	gs.linesmen = get_officials_from_table(linesmen_td.table)
	