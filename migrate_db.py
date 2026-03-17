import sqlite3

"""Database migration helper.

This script updates the existing `database.db` schema to:
- Add `email` (unique) and `phone` columns to `users`.
- Normalize existing email values (strip + lowercase).
- Create unique index on email.
- Add `otp_codes` table for password reset.

Run once after upgrading the app.
"""

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 1) Add columns if missing
# SQLite will error if column exists, so we check PRAGMA table_info.

c.execute("PRAGMA table_info(users)")
cols = [r[1] for r in c.fetchall()]

if "email" not in cols:
    print("Adding column 'email' to users")
    c.execute("ALTER TABLE users ADD COLUMN email TEXT")

if "phone" not in cols:
    print("Adding column 'phone' to users")
    c.execute("ALTER TABLE users ADD COLUMN phone TEXT")

# 2) Normalize emails (strip and lower)
print("Normalizing email fields...")
users = []
for row in c.execute("SELECT id, email FROM users").fetchall():
    uid, email = row
    if email is None:
        continue
    new_email = email.strip().lower()
    if new_email != email:
        users.append((new_email, uid))

for new_email, uid in users:
    c.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, uid))

# 3) Deduplicate emails (keep lowest id)
print("Deduplicating email addresses...")
dups = c.execute(
    "SELECT email FROM users WHERE email IS NOT NULL AND email != '' GROUP BY email HAVING COUNT(*) > 1"
).fetchall()
for (email,) in dups:
    rows = c.execute("SELECT id FROM users WHERE email = ? ORDER BY id", (email,)).fetchall()
    keep = rows[0][0]
    remove_ids = [r[0] for r in rows[1:]]
    print(f"Keeping id={keep} for email={email}, removing {len(remove_ids)} duplicates")
    c.executemany("DELETE FROM users WHERE id = ?", [(rid,) for rid in remove_ids])

# 4) Create unique index on email (ignore if exists)
print("Adding unique index on email...")
try:
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
except Exception as e:
    print("Warning: could not create unique index:", e)

# 5) Create otp_codes table if missing
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='otp_codes'")
if not c.fetchone():
    print("Creating otp_codes table...")
    c.execute(
        """CREATE TABLE otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            otp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )"""
    )

conn.commit()
conn.close()
print("Migration complete.")
