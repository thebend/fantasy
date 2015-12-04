# add project directory to python path
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)

from collection import util

conn = util.get_db_connection()
cursor = conn.cursor()

class SqlTest():
	def __init__(self, title, sql, expectation):
		self.title = title
		self.sql = sql
		self.expectation = expectation
		
	def execute(self):
		try:
			cursor.execute(self.sql)
			self.result = cursor.fetchall()
		except Exception as e:
			self.result = e
		
		self.passed = (self.expectation == self.result)
		operand = '==' if self.passed else '!='
		status = 'Pass' if self.passed else 'Fail'
		print '{title}: {expectation} {operand} {result} ({status})\n{sql}'.format(
			title=self.title,
			expectation=self.expectation,
			operand=operand,
			result=self.result,
			status=status,
			sql=self.sql
		)
		
queries = [
	SqlTest('Create teams', '''INSERT INTO team (team_id, start_date, end_date) VALUES 
(1, '2000-01-01', '2010-01-01')''', 'Test')
]

for i in queries:
	i.execute()