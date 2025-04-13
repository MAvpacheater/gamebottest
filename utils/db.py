import shelve

db = shelve.open("database.db", writeback=True)
