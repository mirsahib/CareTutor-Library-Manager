import sys

from database import get_connection, init_db

SAMPLE_BOOKS = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "category": "Fiction",
        "published_year": 1960,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "category": "Fiction",
        "published_year": 1949,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "category": "Fiction",
        "published_year": 1925,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "category": "Science",
        "published_year": 1988,
        "is_borrowed": 1,
        "borrower_name": "Jane Doe",
    },
    {
        "title": "The Selfish Gene",
        "author": "Richard Dawkins",
        "category": "Science",
        "published_year": 1976,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "Cosmos",
        "author": "Carl Sagan",
        "category": "Science",
        "published_year": 1980,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "SPQR: A History of Ancient Rome",
        "author": "Mary Beard",
        "category": "History",
        "published_year": 2015,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "The Silk Roads",
        "author": "Peter Frankopan",
        "category": "History",
        "published_year": 2015,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "Guns, Germs, and Steel",
        "author": "Jared Diamond",
        "category": "History",
        "published_year": 1997,
        "is_borrowed": 0,
        "borrower_name": None,
    },
    {
        "title": "The Unknown Library Shelf",
        "author": "Anonymous",
        "category": "Uncategorized",
        "published_year": 2020,
        "is_borrowed": 0,
        "borrower_name": None,
    },
]


def seed(reset=False):
    init_db()
    with get_connection() as conn:
        if reset:
            conn.execute("DELETE FROM books")
        else:
            row = conn.execute("SELECT COUNT(*) AS count FROM books").fetchone()
            if row["count"] > 0:
                return 0

        conn.executemany(
            """
            INSERT INTO books (title, author, category, published_year, is_borrowed, borrower_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    book["title"],
                    book["author"],
                    book["category"],
                    book["published_year"],
                    book["is_borrowed"],
                    book["borrower_name"],
                )
                for book in SAMPLE_BOOKS
            ],
        )
        return len(SAMPLE_BOOKS)


def main():
    reset = "--reset" in sys.argv[1:]
    inserted = seed(reset=reset)
    if inserted == 0:
        print("Catalog already populated; nothing to seed.")
    else:
        print(f"Seeded {inserted} books.")


if __name__ == "__main__":
    main()
