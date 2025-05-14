from cs50 import SQL
db = SQL("sqlite:///project.db")
#db.execute(""" CREATE TABLE record (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, score INTEGER NOT NULL);""")
#db.execute("DROP TABLE record;")
columns = db.execute("SELECT name FROM pragma_table_info('record');")
print(columns)
