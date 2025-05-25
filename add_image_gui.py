import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import io

class AddImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Add Face to Database")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.selected_image_path = None
        self.preview_image = None
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = ttk.Label(main_frame, text="Add Face to Database", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Form elements
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Person name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = ttk.Label(name_frame, text="Person Name:", width=15)
        name_label.pack(side=tk.LEFT, padx=5)
        
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Image selection
        image_frame = ttk.Frame(form_frame)
        image_frame.pack(fill=tk.X, pady=5)
        
        image_label = ttk.Label(image_frame, text="Image:", width=15)
        image_label.pack(side=tk.LEFT, padx=5)
        
        self.image_path_var = tk.StringVar()
        self.image_path_entry = ttk.Entry(image_frame, textvariable=self.image_path_var, state="readonly")
        self.image_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = ttk.Button(image_frame, text="Browse", command=self.browse_image)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Image preview
        self.preview_frame = ttk.LabelFrame(main_frame, text="Image Preview")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_button = ttk.Button(button_frame, text="Save to Database", command=self.save_to_database)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Database stats
        self.status_var = tk.StringVar()
        self.update_status()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(side=tk.BOTTOM, pady=5, anchor=tk.W)
    
    def update_status(self):
        """Update the status bar with database stats"""
        try:
            db_path = 'database/faces.db'
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT COUNT(*) FROM faces")
                count = cursor.fetchone()[0]
                conn.close()
                self.status_var.set(f"Database status: {count} faces in database")
            else:
                self.status_var.set("Database status: Database not created yet")
        except Exception as e:
            self.status_var.set(f"Error getting database stats: {e}")
    
    def browse_image(self):
        """Open file dialog to select an image"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.image_path_var.set(file_path)
            
            # Extract name from filename if name field is empty
            if not self.name_entry.get().strip():
                name = os.path.splitext(os.path.basename(file_path))[0].replace('_', ' ')
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, name)
            
            # Update preview
            self.update_preview(file_path)
    
    def update_preview(self, image_path):
        """Update the image preview"""
        try:
            # Open and resize image for preview
            img = Image.open(image_path)
            
            # Calculate new dimensions (max 300x300, maintain aspect ratio)
            width, height = img.size
            max_size = 300
            
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error previewing image: {e}")
            self.preview_label.config(image=None)
    
    def save_to_database(self):
        """Save the image to the database"""
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a person name")
            return
        
        if not self.selected_image_path:
            messagebox.showerror("Error", "Please select an image")
            return
        
        if not os.path.exists(self.selected_image_path):
            messagebox.showerror("Error", "Selected image file not found")
            return
        
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
            
            # Check if person already exists
            cursor = conn.execute("SELECT COUNT(*) FROM faces WHERE name = ?", (name,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                response = messagebox.askyesno(
                    "Confirm", 
                    f"A record for '{name}' already exists. Do you want to add another image for this person?"
                )
                if not response:
                    conn.close()
                    return
            
            # Read the image file as binary
            with open(self.selected_image_path, 'rb') as file:
                photo_data = file.read()
            
            # Store in database
            conn.execute(
                "INSERT INTO faces (name, photo) VALUES (?, ?)",
                (name, photo_data)
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Successfully added {name} to database")
            self.update_status()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding photo to database: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.image_path_var.set("")
        self.selected_image_path = None
        self.preview_label.config(image=None)
        self.preview_image = None

def main():
    root = tk.Tk()
    app = AddImageApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
