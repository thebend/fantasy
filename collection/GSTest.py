from gs import Parser
import NhlReportDownloader

for reportHtml in NhlReportDownloader.get_all_game_report_html('GS'):
	print Parser.parse(reportHtml)
