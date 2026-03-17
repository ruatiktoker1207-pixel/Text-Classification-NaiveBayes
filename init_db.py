import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# bảng user
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# bảng lưu kết quả AI
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
text TEXT,
result TEXT
)
""")

# Dữ liệu huấn luyện bổ sung (do người dùng thêm)
cursor.execute("""
CREATE TABLE IF NOT EXISTS training_data(
id INTEGER PRIMARY KEY AUTOINCREMENT,
text TEXT,
label TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")