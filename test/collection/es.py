import set_path

from datetime import datetime
start_time = datetime.now()

from collection import es
from collection.nhl_reportdownloader import get_all_game_report_html

# 0 for unlimited
iterations = 5
count = 0
for report_html in get_all_game_report_html('GS',2014,(1,2,3)):
	print es.get_from_html(report_html)
	count += 1
	if count == iterations: break

end_time = datetime.now()
execution_time = end_time - start_time
print 'Total execution time: %s' % execution_time