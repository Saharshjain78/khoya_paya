import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import numpy as np

class DatabaseViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Database Viewer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.db_path = 'database/faces.db'
        self.current_faces = []
        self.selected_face_id = None
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Face Database Entries", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create top frame for list and preview
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Face list
        list_frame = ttk.LabelFrame(top_frame, text="Database Entries")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create treeview with scrollbar
        self.tree_frame = ttk.Frame(list_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("id", "name", "count"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("count", text="Images")
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("count", width=60)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_face_select)
        
        # Right side - Face preview
        preview_frame = ttk.LabelFrame(top_frame, text="Face Preview")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="lightgray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image info
        self.info_label = ttk.Label(preview_frame, text="No face selected", font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        # Bottom frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        refresh_button = ttk.Button(button_frame, text="Refresh List", command=self.load_faces)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_face)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        add_button = ttk.Button(button_frame, text="Add New Face", command=self.open_add_interface)
        add_button.pack(side=tk.RIGHT, padx=5)
        
        # Navigation buttons for multiple images of same person
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.show_prev_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.show_next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        self.image_counter = ttk.Label(nav_frame, text="Image 0/0")
        self.image_counter.pack(side=tk.TOP, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.update_status()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(side=tk.BOTTOM, pady=5, anchor=tk.W)
        
        # Initialize
        self.current_image_index = 0
        self.current_person_images = []
        self.load_faces()
    
    def update_status(self):
        """Update the status bar with database stats"""
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT COUNT(*) FROM faces")
                count = cursor.fetchone()[0]
                
                # Get unique names
                cursor = conn.execute("SELECT COUNT(DISTINCT name) FROM faces")
                unique_count = cursor.fetchone()[0]
                
                conn.close()
                self.status_var.set(f"Database status: {count} total images, {unique_count} unique individuals")
            else:
                self.status_var.set("Database status: Database not found")
        except Exception as e:
            self.status_var.set(f"Error getting database stats: {e}")
    
    def load_faces(self):
        """Load faces from the database into the treeview"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_faces = []
        
        try:
            if not os.path.exists(self.db_path):
                messagebox.showinfo("Database Not Found", "Face database not found. Please add faces first.")
                return
            
            conn = sqlite3.connect(self.db_path)
            
            # Get all unique names and count of images for each
            cursor = conn.execute("""
                SELECT name, COUNT(*) as count FROM faces
                GROUP BY name ORDER BY name
            """)
            
            # Add to treeview
            for i, (name, count) in enumerate(cursor):
                self.tree.insert("", tk.END, values=(i+1, name, count))
                self.current_faces.append(name)
            
            conn.close()
            self.update_status()
            
            # Clear preview
            self.clear_preview()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading faces: {e}")
    
    def on_face_select(self, event):
        """Handle selection of a face in the treeview"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        selected_name = item['values'][1]  # Name is in the second column
        
        # Load all images for this person
        self.load_person_images(selected_name)
    
    def load_person_images(self, name):
        """Load all images for a selected person"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT id, photo FROM faces WHERE name = ?", (name,))
            
            self.current_person_images = []
            for row in cursor:
                face_id, photo_blob = row
                self.current_person_images.append((face_id, photo_blob))
            
            conn.close()
            
            if self.current_person_images:
                self.current_image_index = 0
                self.display_current_image()
                self.update_navigation_buttons()
            else:
                self.clear_preview()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading images: {e}")
    
    def display_current_image(self):
        """Display the current image in the preview"""
        if not self.current_person_images or self.current_image_index >= len(self.current_person_images):
            self.clear_preview()
            return
        
        face_id, photo_blob = self.current_person_images[self.current_image_index]
        self.selected_face_id = face_id
        
        try:
            # Convert BLOB to image
            image = Image.open(io.BytesIO(photo_blob))
            
            # Get preview dimensions
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # If canvas has no size yet, use reasonable defaults
            if canvas_width < 10:
                canvas_width = 300
            if canvas_height < 10:
                canvas_height = 300
            
            # Resize image for preview
            width, height = image.size
            ratio = min(canvas_width/width, canvas_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Resize and convert to PhotoImage
            image = image.resize((new_width, new_height), Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(image)
            
            # Display on canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width//2, canvas_height//2,
                image=self.photo_image, anchor=tk.CENTER
            )
            
            # Update info
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                name = item['values'][1]
                self.info_label.config(text=f"Name: {name} (ID: {face_id})")
                
                # Update image counter
                self.image_counter.config(
                    text=f"Image {self.current_image_index+1}/{len(self.current_person_images)}"
                )
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error displaying image: {e}")
    
    def clear_preview(self):
        """Clear the preview area"""
        self.preview_canvas.delete("all")
        self.info_label.config(text="No face selected")
        self.image_counter.config(text="Image 0/0")
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.selected_face_id = None
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        if len(self.current_person_images) <= 1:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL if self.current_image_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_image_index < len(self.current_person_images)-1 else tk.DISABLED)
    
    def show_prev_image(self):
        """Show the previous image for the selected person"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def show_next_image(self):
        """Show the next image for the selected person"""
        if self.current_image_index < len(self.current_person_images) - 1:
            self.current_image_index += 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def delete_face(self):
        """Delete the selected face from the database"""
        if not self.selected_face_id:
            messagebox.showinfo("No Selection", "Please select a face to delete.")
            return
        
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        name = item['values'][1]
        
        # Ask for confirmation
        response = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete this image of {name}?\nThis cannot be undone."
        )
        
        if response:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("DELETE FROM faces WHERE id = ?", (self.selected_face_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Face deleted successfully.")
                
                # Reload current person's images
                self.load_person_images(name)
                
                # If no more images, refresh the whole list
                if not self.current_person_images:
                    self.load_faces()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting face: {e}")
    
    def open_add_interface(self):
        """Open the add image interface"""
        try:
            # Check if add_image_gui module exists
            import importlib.util
            spec = importlib.util.find_spec('add_image_gui')
            
            if spec is None:
                messagebox.showerror("Error", "add_image_gui.py not found. Please make sure it exists.")
                return
                
            import add_image_gui
            
            # Create a new window for adding images
            add_window = tk.Toplevel(self.root)
            add_app = add_image_gui.AddImageApp(add_window)
            
            # Set up a callback to refresh our view when the add window is closed
            add_window.protocol("WM_DELETE_WINDOW", 
                               lambda: [add_window.destroy(), self.load_faces()])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening add interface: {e}")

def main():
    root = tk.Tk()
    app = DatabaseViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
