import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Fix corrupted records
cursor.execute("UPDATE predictions SET result='neutral' WHERE result NOT IN ('positive','negative','neutral')")
conn.commit()

# Show the fixed data
cursor.execute('SELECT result, COUNT(*) FROM predictions GROUP BY result')
stats = cursor.fetchall()
print("Predictions after fix:")
for result, count in stats:
    print(f"  {result}: {count}")

conn.close()
