from gs import Parser
import NhlReportDownloader

iterations = 1
count = 0
for report_html in NhlReportDownloader.get_all_game_report_html('GS'):
	print Parser.parse(report_html)
	count += 1
	if count > iterations: break