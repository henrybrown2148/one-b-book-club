import sqlite3

conn = sqlite3.connect("bookclub.db")
cursor = conn.cursor()

books = [
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy adventure"),
    ("1984", "George Orwell", "Dystopian fiction"),
    ("Dune", "Frank Herbert", "Science fiction")
]

cursor.executemany("""
INSERT INTO books
(title, author, description)
VALUES (?, ?, ?)
""", books)

conn.commit()
conn.close()

print("Books added!")