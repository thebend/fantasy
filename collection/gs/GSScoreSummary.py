from GSGoal import GSGoal

def get_player_list_from_text(txt):
	""" return int array from text like '13, 20, 21, 31, 55' """
	return [int(i) for i in txt.split(', ')]

def set_scoring_summary(soup, gs):
	# td with text "SCORING SUMMARY"
	title_td = soup.find('td',text='SCORING SUMMARY')
	# parent tr, parent table, parent td, parent tr
	title_parent_tr = title_td.parent.parent.parent.parent
	# next tr, td, table
	scoring_summary_table = title_parent_tr.find_next_sibling('tr').td.table
	# all trs except first, which is a label
	
	for tr in scoring_summary_table('tr')[1:]:
		(goal_number, period, time, strength, team, scorer, assist1, assist2, visitors, home) = [td.text.strip() for td in tr('td')]
		
		g = GSGoal()
		g.period = period
		g.time = time
		# g.strength can be inferred from home/visitors count
		g.team = team
		# like "13 C.ATKINSON(1)"
		g.scorer = int(scorer.split(' ')[0])
		try:
			g.assist1 = int(assist1.split(' ')[0])
			g.assist2 = int(assist2.split(' ')[0])
		except ValueError:
			# it's normal that sometimes we won't have assists		
			pass
		g.visitors = get_player_list_from_text(visitors)
		g.home = get_player_list_from_text(home)
		gs.goals.append(g)
