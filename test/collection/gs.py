# add project directory to python path
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)

from collection.gs import gs_parser
from collection.nhl_reportdownloader import get_all_game_report_html

# 0 for unlimited
iterations = 0
count = 0
for report_html in get_all_game_report_html('GS',2014,3):
	print gs_parser.parse(report_html).get_goal_table_string()
	count += 1
	if count == iterations: break
