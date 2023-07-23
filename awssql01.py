import pymysql

db = pymysql.connect(host='database-1.cdatmsjowfie.us-east-1.rds.amazonaws.com',user='admin',password='awsmysql02',database="db01")

cursor = db.cursor()

cursor

query = '''
SELECT SUM(SALES) AS 2004_SALES FROM sales WHERE PRODUCTLINE = 'Motorcycles' AND YEAR_ID = 2004 
UNION 
SELECT SUM(SALES) AS 2005_SALES  FROM sales WHERE PRODUCTLINE = 'Motorcycles' AND YEAR_ID = 2005
'''

cursor.execute(query)

data = cursor.fetchall()

print(data)

