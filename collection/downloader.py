import requests
import threading
import Queue
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('fantasy.conf')

def get_html(url):
		response = requests.get(url)
		
		# if page not found, we tried loading a game that wasn't reported
		if response.status_code == 404:
			return None
		else:
			return response.text
	
def html_downloader(url_queue, response_queue):
	while True:
		try:
			url = url_queue.get(block=False)
			html = get_html(url)
			response_queue.put(html)
		except Queue.Empty:
			# done once queue is empty
			break

def get_all_html(urls):
	"""
	Yield HTML of all specified reports
	"""
	# create queue with all urls to parse
	url_queue = Queue.Queue()
	for url in urls:
		url_queue.put(url)
	# note number of urls so we know when finished
	urls_active = url_queue.qsize()
	
	# start threads to download and parse data
	response_queue = Queue.Queue()
	threads = []
	for i in range(config.getint('nhl','concurrent_connections')):
		t = threading.Thread(target=html_downloader, args=(url_queue, response_queue))
		t.daemon = True
		threads.append(t)
		t.start()
	
	# yield all data as it comes in
	while urls_active > 0:
		html = response_queue.get()
		urls_active -= 1
		if html:
			yield html
