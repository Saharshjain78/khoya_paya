import sqlite3
import os

def verify_database():
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.execute("SELECT name FROM faces")
    
    print("Names in database:")
    for row in cursor:
        print(f"- {row[0]}")
    
    # Get count of entries
    cursor = conn.execute("SELECT COUNT(*) FROM faces")
    count = cursor.fetchone()[0]
    print(f"\nTotal entries in database: {count}")
    
    conn.close()

if __name__ == "__main__":
    verify_database() 