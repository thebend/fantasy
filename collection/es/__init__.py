from bs4 import BeautifulSoup

def get_from_html(html):
	soup = BeautifulSoup(html, 'html.parser')
	data_table = soup.table('tr', recursive=False)[7].table
	# .tag is equal to .find('tag').  ('tag') is equal to .find_all('tag').
	# below line is equivalent to above line, for example
	# data_table = soup.find('table').find_all('tr', recursive=False)[7].find('table')
	
	# start with away team
	away = True
	
	# display a header to make output more readable
	print 'T P# P Player Name            G A P +- PN PIM   TOT SHF   AVG    PP    SH    EV  S AB MS TH GV TK BS FW FL  F%'
	# first two rows just contain headings
	for tr in data_table('tr', recursive=False)[2:]:
		try:
			# rows starting with integers (player numbers) have relevant data
			int(tr.td.text)
		except ValueError:
			# Once we hit rows that don't start with numbers
			# we are at the summary lines between teams
			# and further player data will be for the home team
			away = False
			# since this line is invalid, go to next line instead of doing below processing
			continue
			
		(
			num, pos, name, g, a, p, pm, pn, pim,
			tot, shf, avg, pp, sh, ev,
			s, ab, ms, th, gv, tk, bs, fw, fl, fp
		) = [td.text.strip() for td in tr('td')]
		
		# accented E in French name could be preserved in database,
		# but printing to console, which only supports ASCII,
		# requires replacing it with a regular E first
		name = name.encode('utf8').replace('\xc3\x89','E')
		
		# could convert +/- values into numbers
		# when empty, throws an error, so could overwrite to
		# preserve being empty, or just save as 0
		try:
			pm = int(pm)
		except:
			pm = ''
		
		print '{:1} {:>2} {:1} {:22} {:1} {:1} {:1} {:>2} {:>2} {:>3} {:>5} {:>3} {:>5} {:>5} {:>5} {:>5} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>3}'.format(
			'A' if away else 'H',
			num, pos, name.encode('ascii','replace'), g, a, p, pm, pn, pim,
			tot, shf, avg, pp, sh, ev,
			s, ab, ms, th, gv, tk, bs, fw, fl, fp
		)
			
import requests
url = 'http://www.nhl.com/scores/htmlreports/20142015/ES010001.HTM'
response = requests.get(url)
get_from_html(response.text)