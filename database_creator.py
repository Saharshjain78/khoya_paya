import os
import sqlite3
from pathlib import Path

class DatabaseCreator:
    def __init__(self, db_path: str = 'database/faces.db', photos_dir: str = 'photos'):
        self.db_path = db_path
        self.photos_dir = photos_dir
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    photo BLOB NOT NULL
                )
            ''')
    
    def add_photo(self, name: str, photo_path: str):
        try:
            # Read the image file as binary
            with open(photo_path, 'rb') as file:
                photo_data = file.read()
            
            # Store in database
            with self.conn:
                self.conn.execute(
                    "INSERT INTO faces (name, photo) VALUES (?, ?)",
                    (name, photo_data)
                )
            print(f"Added {name} to database")
            
        except Exception as e:
            print(f"Error adding photo for {name}: {e}")
    
    def process_photos_directory(self):
        # Get all image files from the photos directory
        valid_extensions = ('.jpg', '.jpeg', '.png')
        
        for file in os.listdir(self.photos_dir):
            if file.lower().endswith(valid_extensions):
                # Get the name from filename (remove extension and replace underscores with spaces)
                name = os.path.splitext(file)[0].replace('_', ' ')
                photo_path = os.path.join(self.photos_dir, file)
                
                self.add_photo(name, photo_path)
    
    def close(self):
        self.conn.close()

def main():
    # Initialize and run the database creator
    creator = DatabaseCreator()
    creator.process_photos_directory()
    creator.close()
    print("Database creation completed!")

if __name__ == "__main__":
    main() 