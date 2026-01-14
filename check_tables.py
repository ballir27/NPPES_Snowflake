import duckdb

con = duckdb.connect('nppes.duckdb')
tables = con.execute("SHOW TABLES").fetchall()
print(tables)
