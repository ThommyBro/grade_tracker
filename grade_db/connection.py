import sqlite3
from pathlib import Path

# ------- Create Connection for all repos ------- #

db_path = Path(__file__).parent / "grade.db"    # creates grade.db in the same folder as this file (if it not exists)

def create_connection() -> sqlite3.Connection:
    """
    Create a database connection to grade.db
    If the file not exists it will be generated.
    """
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON") 
    return con
