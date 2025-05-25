import os
import sqlite3
import sys
from pathlib import Path

def add_image_to_database(image_path, name=None):
    """
    Add a single image to the database.
    If name is not provided, it will be extracted from the filename.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return False
    
    # Extract name from filename if not provided
    if name is None:
        name = os.path.splitext(os.path.basename(image_path))[0].replace('_', ' ')
    
    # Ensure database directory exists
    db_path = 'database/faces.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Create table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                photo BLOB NOT NULL
            )
        ''')
        
        # Read the image file as binary
        with open(image_path, 'rb') as file:
            photo_data = file.read()
        
        # Check if the exact same person's photo already exists
        cursor = conn.execute("SELECT COUNT(*) FROM faces WHERE name = ?", (name,))
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            response = input(f"A record for '{name}' already exists. Add anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                conn.close()
                return False
        
        # Store in database
        conn.execute(
            "INSERT INTO faces (name, photo) VALUES (?, ?)",
            (name, photo_data)
        )
        conn.commit()
        print(f"Successfully added {name} to database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding photo: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_image.py <image_path> [person_name]")
        print("Example: python add_image.py photos/john_doe.jpg 'John Doe'")
        return
    
    image_path = sys.argv[1]
    name = None
    
    if len(sys.argv) >= 3:
        name = sys.argv[2]
    
    add_image_to_database(image_path, name)

if __name__ == "__main__":
    main()
