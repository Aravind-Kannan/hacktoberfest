import sqlite3
from api import db_loc


def main():
    conn = sqlite3.connect(db_loc)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE "todo_tasks" (
        "id"	INTEGER,
        "descr"	TEXT NOT NULL,
        "status"	TEXT NOT NULL CHECK("status" IN ('NOT STARTED', 'IN PROGRESS', 'FINISHED')),
        "due_date"	TEXT NOT NULL,
        PRIMARY KEY("id")
    )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
