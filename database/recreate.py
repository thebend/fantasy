import os
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('fantasy.conf')

password_cmd = 'set PGPASSWORD={}'.format(config.get('database','password')) 
cmd = 'psql -f database/fantasy.postgres.sql -h {} -p {} -d {} -U {}'.format(
	config.get('database','host'),
	config.get('database','port'),
	config.get('database','database'),
	config.get('database','username')
)
# setting password this way doesn't always seem to work?
os.system(password_cmd)
os.system(cmd)
