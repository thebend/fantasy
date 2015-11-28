# add project directory to python path
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)

from collection.gs import gs_parser
from collection import nhl_reportdownloader

iterations = 1
count = 0
for report_html in nhl_reportdownloader.get_all_game_report_html('GS'):
	count += 1
	if count > iterations: break
	print gs_parser.parse(report_html)
