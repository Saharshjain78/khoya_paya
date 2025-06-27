# filepath: c:\Users\Asus\Documents\Projects\khoya_paya\advanced_face_app_enhanced_fixed.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import sqlite3
import io
import hashlib
import json
import pandas as pd
from datetime import datetime
import face_recognition
import time
import tempfile
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="Advanced Face Recognition System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'show_profile_id' not in st.session_state:
    st.session_state.show_profile_id = None
if 'show_profile_name' not in st.session_state:
    st.session_state.show_profile_name = None

# Create necessary directories
os.makedirs('database', exist_ok=True)
os.makedirs('known_faces', exist_ok=True)
os.makedirs('user_profiles', exist_ok=True)

class DatabaseManager:
    def __init__(self):
        self.db_path = 'database/advanced_faces.db'
        self.init_database()
    
    def get_connection(self):
        """Create a database connection"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table for login system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                profile_data TEXT
            )
        ''')
        
        # Faces table for face recognition with enhanced profile information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                photo BLOB NOT NULL,
                encoding BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                added_by TEXT,
                tags TEXT,
                age INTEGER,
                occupation TEXT,
                department TEXT,
                contact_info TEXT,
                last_seen DATETIME,
                scan_count INTEGER DEFAULT 0,
                profile_data TEXT
            )
        ''')
        
        # Recognition logs table with enhanced tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recognition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                face_id INTEGER,
                recognized_person TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                location TEXT,
                device_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (face_id) REFERENCES faces (id)
            )
        ''')
        
        # Face scan history table for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face_id INTEGER,
                scanned_by_user INTEGER,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                FOREIGN KEY (face_id) REFERENCES faces (id),
                FOREIGN KEY (scanned_by_user) REFERENCES users (id)
            )
        ''')
        
        # User profiles table for individual recognition history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                recognized_faces TEXT,
                total_recognitions INTEGER DEFAULT 0,
                last_recognition DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_password = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, user_type, profile_data)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin', '{}'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, user_type, profile_data 
            FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'user_type': user[2],
                'profile_data': json.loads(user[3] or '{}')
            }
        return None
    
    def create_user(self, username: str, password: str, user_type: str = 'user') -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, user_type, profile_data)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, user_type, '{}'))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, user_type, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'user_type': row[2],
                'created_at': row[3],
                'last_login': row[4]
            })
        
        conn.close()
        return users
    
    def update_last_login(self, user_id: int):
        """Update user's last login time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()

class FaceRecognitionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def encode_face_from_image(self, image):
        """Extract face encoding from image using face_recognition library"""
        try:
            if isinstance(image, Image.Image):
                # Convert PIL image to RGB if it's not already
                if image.mode == 'RGBA':
                    # Convert RGBA to RGB by creating a white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                    image = background
                elif image.mode not in ['RGB', 'L']:
                    # Convert any other mode to RGB
                    image = image.convert('RGB')
                
                image_array = np.array(image)
            else:
                image_array = image
            
            # Ensure the image is in the correct data type
            if image_array.dtype != np.uint8:
                if image_array.dtype in [np.float32, np.float64]:
                    # If it's floating point, assume it's normalized to 0-1
                    image_array = (image_array * 255).astype(np.uint8)
                else:
                    # For other types, just convert to uint8
                    image_array = image_array.astype(np.uint8)
            
            # Handle different image shapes
            if len(image_array.shape) == 3:
                if image_array.shape[2] == 4:  # RGBA
                    # Convert RGBA to RGB
                    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
                elif image_array.shape[2] == 3:  # RGB or BGR
                    # Check if it's BGR and convert to RGB
                    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                else:
                    return None, f"Unsupported number of channels: {image_array.shape[2]}"
            elif len(image_array.shape) == 2:  # Grayscale
                # Convert grayscale to RGB
                rgb_image = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            else:
                return None, f"Unsupported image shape: {image_array.shape}"
            
            # Ensure the image is 8-bit
            if rgb_image.dtype != np.uint8:
                rgb_image = rgb_image.astype(np.uint8)
            
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return None, "No face detected in the image"
            
            if len(face_locations) > 1:
                return None, "Multiple faces detected. Please use an image with only one face"
            
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) > 0:
                return face_encodings[0], None
            else:
                return None, "Could not encode the face"
                
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def add_face_to_database(self, name: str, image, description: str = "", added_by: str = "", 
                           age: int = None, occupation: str = "", department: str = "", 
                           contact_info: str = "", profile_data: dict = None):
        """Add a face to the database with enhanced profile information"""
        try:
            encoding, error = self.encode_face_from_image(image)
            if error:
                return False, error
            
            # Convert image to bytes
            if isinstance(image, Image.Image):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
            else:
                is_success, buffer = cv2.imencode('.png', image)
                if is_success:
                    img_bytes = buffer.tobytes()
                else:
                    return False, "Failed to encode image"
            
            # Convert encoding to bytes
            encoding_bytes = encoding.tobytes()
            
            # Convert profile_data to JSON
            profile_json = json.dumps(profile_data) if profile_data else None
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO faces (name, photo, encoding, description, added_by, tags, 
                                 age, occupation, department, contact_info, scan_count, profile_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            ''', (name, img_bytes, encoding_bytes, description, added_by, "", 
                  age, occupation, department, contact_info, profile_json))
            
            conn.commit()
            conn.close()
            return True, "Face added successfully"
            
        except sqlite3.IntegrityError:
            return False, "A person with this name already exists"
        except Exception as e:
            return False, f"Error adding face: {str(e)}"
    
    def recognize_face(self, image, tolerance: float = 0.6):
        """Recognize a face from the database with enhanced tracking"""
        try:
            encoding, error = self.encode_face_from_image(image)
            if error:
                return None, error, 0.0, None
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name, encoding FROM faces')
            faces_data = cursor.fetchall()
            
            if not faces_data:
                conn.close()
                return None, "No faces in database", 0.0, None
            
            known_encodings = []
            known_names = []
            face_ids = []
            
            for face_id, name, encoding_bytes in faces_data:
                known_encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                known_encodings.append(known_encoding)
                known_names.append(name)
                face_ids.append(face_id)
            
            if len(known_encodings) == 0:
                conn.close()
                return None, "No valid encodings in database", 0.0, None
            
            # Calculate distances
            distances = face_recognition.face_distance(known_encodings, encoding)
            min_distance = min(distances)
            best_match_index = np.argmin(distances)
            
            if min_distance <= tolerance:
                confidence = (1 - min_distance) * 100
                matched_face_id = face_ids[best_match_index]
                matched_name = known_names[best_match_index]
                
                # Update face scan statistics
                cursor.execute('''
                    UPDATE faces 
                    SET scan_count = scan_count + 1, last_seen = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (matched_face_id,))
                
                conn.commit()
                conn.close()
                return matched_name, None, confidence, matched_face_id
            else:
                conn.close()
                return None, "No match found", 0.0, None
                
        except Exception as e:
            return None, f"Error during recognition: {str(e)}", 0.0, None
    
    def get_all_faces(self):
        """Get all faces from database with enhanced profile information"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, timestamp, added_by, tags, 
                   age, occupation, department, contact_info, last_seen, scan_count, profile_data
            FROM faces
            ORDER BY timestamp DESC
        ''')
        
        faces = []
        for row in cursor.fetchall():
            faces.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'timestamp': row[3],
                'added_by': row[4],
                'tags': row[5],
                'age': row[6],
                'occupation': row[7],
                'department': row[8],
                'contact_info': row[9],
                'last_seen': row[10],
                'scan_count': row[11],
                'profile_data': json.loads(row[12]) if row[12] else {}
            })
        
        conn.close()
        return faces
    
    def log_recognition(self, user_id: int, recognized_person: str, confidence: float, 
                       method: str, face_id: int = None, location: str = "", device_info: str = ""):
        """Log recognition event with enhanced tracking"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Log recognition
        cursor.execute('''
            INSERT INTO recognition_logs (user_id, face_id, recognized_person, confidence, method, location, device_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, face_id, recognized_person, confidence, method, location, device_info))
        
        # Log face scan history if face_id is provided
        if face_id:
            cursor.execute('''
                INSERT INTO face_scan_history (face_id, scanned_by_user, confidence, method)
                VALUES (?, ?, ?, ?)
            ''', (face_id, user_id, confidence, method))
        
        conn.commit()
        conn.close()
    
    def get_face_profile(self, face_id: int):
        """Get detailed face profile information with scan history"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get face information
        cursor.execute('''
            SELECT id, name, description, timestamp, added_by, tags,
                   age, occupation, department, contact_info, last_seen, scan_count, profile_data
            FROM faces WHERE id = ?
        ''', (face_id,))
        
        face_data = cursor.fetchone()
        if not face_data:
            conn.close()
            return None
        
        face_profile = {
            'id': face_data[0],
            'name': face_data[1],
            'description': face_data[2],
            'timestamp': face_data[3],
            'added_by': face_data[4],
            'tags': face_data[5],
            'age': face_data[6],
            'occupation': face_data[7],
            'department': face_data[8],
            'contact_info': face_data[9],
            'last_seen': face_data[10],
            'scan_count': face_data[11],
            'profile_data': json.loads(face_data[12]) if face_data[12] else {}
        }
        
        # Get recent scan history
        cursor.execute('''
            SELECT fsh.timestamp, fsh.confidence, fsh.method, u.username
            FROM face_scan_history fsh
            LEFT JOIN users u ON fsh.scanned_by_user = u.id
            WHERE fsh.face_id = ?
            ORDER BY fsh.timestamp DESC
            LIMIT 10
        ''', (face_id,))
        
        scan_history = cursor.fetchall()
        face_profile['scan_history'] = scan_history
        
        conn.close()
        return face_profile
    
    def update_user_profile(self, user_id: int, recognized_person: str):
        """Update user profile with recognition data"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get existing profile
        cursor.execute('''
            SELECT recognized_faces, total_recognitions 
            FROM user_profiles 
            WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        
        if profile:
            recognized_faces = json.loads(profile[0] or '[]')
            if recognized_person not in recognized_faces:
                recognized_faces.append(recognized_person)
            
            cursor.execute('''
                UPDATE user_profiles 
                SET recognized_faces = ?, total_recognitions = ?, last_recognition = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (json.dumps(recognized_faces), profile[1] + 1, user_id))
        else:
            cursor.execute('''
                INSERT INTO user_profiles (user_id, recognized_faces, total_recognitions, last_recognition)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                ''', (user_id, json.dumps([recognized_person])))
        
        conn.commit()
        conn.close()
    
    def get_face_scan_history(self, face_id: int, limit: int = 50):
        """Get detailed scan history for a face including user info and timestamps"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fsh.timestamp, fsh.confidence, fsh.method, u.username, u.user_type,
                   rl.location, rl.device_info
            FROM face_scan_history fsh
            LEFT JOIN users u ON fsh.scanned_by_user = u.id
            LEFT JOIN recognition_logs rl ON (rl.face_id = fsh.face_id AND rl.timestamp = fsh.timestamp)
            WHERE fsh.face_id = ?
            ORDER BY fsh.timestamp DESC
            LIMIT ?
        ''', (face_id, limit))
        
        scan_history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'confidence': row[1],
                'method': row[2],
                'username': row[3] or 'Unknown',
                'user_type': row[4] or 'Unknown',
                'location': row[5] or '',
                'device_info': row[6] or ''
            }
            for row in scan_history
        ]

# Initialize managers
db_manager = DatabaseManager()
face_manager = FaceRecognitionManager(db_manager)

def login_page():
    """Login page"""
    st.title("🔐 Kidnapping Prevention System")
    st.markdown("### Welcome! Please sign in or create a new account")
    st.markdown("---")
    
    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)
    
    # Login form in left column
    with col1:
        st.subheader("🚪 Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🔓 Sign In", use_container_width=True)
            
            if login_button:
                if username and password:
                    user = db_manager.verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_type = user['user_type']
                        st.session_state.current_user = user
                        db_manager.update_last_login(user['id'])
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
       
    # Registration form in right column
    with col2:
        st.subheader("📝 Create New Account")
        
        with st.form("register_form"):
            new_username = st.text_input("New Username", placeholder="Choose a username")
            new_password = st.text_input("New Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_button = st.form_submit_button("📋 Register", use_container_width=True)
            
            if register_button:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        if db_manager.create_user(new_username, new_password, 'user'):
                            st.success("✅ Account created successfully! You can now sign in.")
                        else:
                            st.error("❌ Username already exists")
                    else:
                        st.error("❌ Passwords do not match")
                else:
                    st.error("❌ Please fill all fields")
        
        # Registration info
        st.info("ℹ️ **New users** are created with regular user privileges")
        
def display_face_profile(face_id: int, face_name: str):
    """Display detailed face profile with scan history (admin only)"""
    if st.session_state.user_type != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    st.subheader(f"👤 Profile: {face_name}")
    
    # Get face profile
    profile = face_manager.get_face_profile(face_id)
    if not profile:
        st.error("Profile not found")
        return
    
    # Basic profile information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Information")
        st.write(f"**Name:** {profile['name']}")
        if profile.get('age'):
            st.write(f"**Age:** {profile['age']}")
        if profile.get('occupation'):
            st.write(f"**Occupation:** {profile['occupation']}")
        if profile.get('department'):
            st.write(f"**Department:** {profile['department']}")
        if profile.get('contact_info'):
            st.write(f"**Contact:** {profile['contact_info']}")
        if profile.get('description'):
            st.write(f"**Description:** {profile['description']}")
        
        st.markdown("### Database Info")
        st.write(f"**Added:** {profile['timestamp']}")
        if profile.get('added_by'):
            st.write(f"**Added by:** {profile['added_by']}")
    
    with col2:
        st.markdown("### Scan Statistics")
        st.metric("Total Scans", profile.get('scan_count', 0))
        if profile.get('last_seen'):
            st.write(f"**Last Seen:** {profile['last_seen']}")
        
        # Get detailed scan history
        scan_history = face_manager.get_face_scan_history(face_id)
        st.metric("Detailed Records", len(scan_history))
    
    # Detailed scan history
    st.markdown("### 📊 Detailed Scan History")
    st.markdown("*All instances when this face was spotted, along with user information*")
    
    if scan_history:
        # Show detailed scan history in expandable sections
        for i, scan in enumerate(scan_history):
            with st.expander(f"Scan #{i+1} - {scan['timestamp'][:19]} by {scan['username']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Scan Details**")
                    st.write(f"Timestamp: {scan['timestamp']}")
                    st.write(f"Confidence: {scan['confidence']:.2f}%")
                    st.write(f"Method: {scan['method']}")
                
                with col2:
                    st.write("**User Information**")
                    st.write(f"Username: {scan['username']}")
                    st.write(f"User Type: {scan['user_type']}")
                
                with col3:
                    st.write("**Additional Info**")
                    if scan['location']:
                        st.write(f"Location: {scan['location']}")
                    if scan['device_info']:
                        st.write(f"Device: {scan['device_info']}")
        
        # Export option
        if len(scan_history) > 0:
            st.markdown("### 📥 Export Data")
            export_df = pd.DataFrame(scan_history)
            csv_data = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Scan History (CSV)",
                data=csv_data,
                file_name=f"{face_name}_scan_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No scan history available for this face.")

def admin_dashboard():
    """Admin dashboard with full control"""
    st.title("👨‍💼 Admin Dashboard")
    
    # Sidebar for admin functions
    with st.sidebar:
        st.subheader("Admin Functions")
        admin_action = st.selectbox(
            "Select Action",
            ["User Management", "Face Database", "System Analytics", "Recognition Logs", "User Profiles"]
        )
    
    if admin_action == "User Management":
        st.subheader("👥 User Management")
        
        # Create new user
        with st.expander("Create New User"):
            with st.form("create_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                user_type = st.selectbox("User Type", ["user", "admin"])
                create_button = st.form_submit_button("Create User")
                
                if create_button:
                    if new_username and new_password:
                        if db_manager.create_user(new_username, new_password, user_type):
                            st.success(f"User '{new_username}' created successfully!")
                        else:
                            st.error("Username already exists")
        
        # Display all users
        st.subheader("All Users")
        users = db_manager.get_all_users()
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")
    
    elif admin_action == "Face Database":
        face_database_management()
    
    elif admin_action == "System Analytics":
        system_analytics()
    
    elif admin_action == "Recognition Logs":
        recognition_logs()
    
    elif admin_action == "User Profiles":
        user_profiles_admin()

def user_dashboard():
    """User dashboard with photo capture and recognition"""
    st.title("👤 User Dashboard")
    
    user = st.session_state.current_user
    st.write(f"Welcome, **{user['username']}**!")
    
    # Sidebar for user functions
    with st.sidebar:
        st.subheader("User Functions")
        user_action = st.selectbox(
            "Select Action",
            ["Photo Recognition", "Live Recognition", "My Profile", "Recognition History"]
        )
    
    if user_action == "Photo Recognition":
        photo_recognition()
    elif user_action == "Live Recognition":
        live_recognition()
    elif user_action == "My Profile":
        user_profile()
    elif user_action == "Recognition History":
        user_recognition_history()

def photo_recognition():
    """Photo upload and recognition feature"""
    st.subheader("📷 Photo Recognition")
    
    uploaded_file = st.file_uploader(
        "Upload an image for recognition",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif', 'webp'],
        help="Upload an image containing a face to recognize (supports JPG, PNG, BMP, TIFF, WebP)"
    )
    
    if uploaded_file is not None:
        try:
            # Open and validate the image
            image = Image.open(uploaded_file)
            
            # Display image info for debugging
            st.info(f"Image format: {image.format}, Mode: {image.mode}, Size: {image.size}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)
            
            with col2:
                if st.button("🔍 Recognize Face", type="primary"):
                    with st.spinner("Recognizing face..."):
                        result = face_manager.recognize_face(image)
                        name, error, confidence, face_id = result
                        
                        if error:
                            st.error(f"Recognition failed: {error}")
                        elif name:
                            st.success(f"✅ **Recognized: {name}**")
                            st.info(f"Confidence: {confidence:.2f}%")
                            st.info(f"🕐 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # Log the recognition with face ID
                            face_manager.log_recognition(
                                st.session_state.current_user['id'],
                                name,
                                confidence,
                                "photo_upload",
                                face_id,
                                "Web App",
                                "Browser Upload"
                            )
                            
                            # Update user profile
                            face_manager.update_user_profile(st.session_state.current_user['id'], name)
                            
                            # Display face profile information
                            if face_id:
                                profile = face_manager.get_face_profile(face_id)
                                if profile:
                                    st.markdown("### 👤 Profile Information")
                                    
                                    # Basic profile info
                                    if profile.get('age'):
                                        st.write(f"**Age:** {profile['age']}")
                                    if profile.get('occupation'):
                                        st.write(f"**Occupation:** {profile['occupation']}")
                                    if profile.get('department'):
                                        st.write(f"**Department:** {profile['department']}")
                                    if profile.get('contact_info'):
                                        st.write(f"**Contact:** {profile['contact_info']}")
                                    
                                    # Scan statistics
                                    st.write(f"**Total Scans:** {profile.get('scan_count', 0)}")
                                    if profile.get('last_seen'):
                                        st.write(f"**Last Seen:** {profile['last_seen']}")
                            
                            st.balloons()
                        else:
                            st.warning("❌ No matching face found in database")
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

def live_recognition():
    """Live camera recognition feature"""
    st.subheader("📹 Live Recognition")
    
    st.info("📌 Use your camera to capture and recognize faces in real-time")
    
    # Camera input
    camera_input = st.camera_input("Take a picture for recognition")
    
    if camera_input is not None:
        try:
            image = Image.open(camera_input)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, caption="Captured Image", use_container_width=True)
            
            with col2:
                with st.spinner("Recognizing face..."):
                    result = face_manager.recognize_face(image)
                    name, error, confidence, face_id = result
                    
                    if error:
                        st.error(f"Recognition failed: {error}")
                    elif name:
                        st.success(f"✅ **Recognized: {name}**")
                        st.info(f"Confidence: {confidence:.2f}%")
                        st.info(f"🕐 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Log the recognition with face ID
                        face_manager.log_recognition(
                            st.session_state.current_user['id'],
                            name,
                            confidence,
                            "live_camera",
                            face_id,
                            "Web App Camera",
                            "Live Camera Feed"
                        )
                        
                        # Update user profile
                        face_manager.update_user_profile(st.session_state.current_user['id'], name)
                        
                        # Display face profile information
                        if face_id:
                            profile = face_manager.get_face_profile(face_id)
                            if profile:
                                st.markdown("### 👤 Profile Information")
                                
                                # Basic profile info
                                if profile.get('age'):
                                    st.write(f"**Age:** {profile['age']}")
                                if profile.get('occupation'):
                                    st.write(f"**Occupation:** {profile['occupation']}")
                                if profile.get('department'):
                                    st.write(f"**Department:** {profile['department']}")
                                
                                # Scan statistics
                                st.write(f"**Total Scans:** {profile.get('scan_count', 0)}")
                                if profile.get('last_seen'):
                                    st.write(f"**Last Seen:** {profile['last_seen']}")
                        
                        st.balloons()
                    else:
                        st.warning("❌ No matching face found in database")
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

def face_database_management():
    """Face database management (admin feature)"""
    st.subheader("🗄️ Face Database Management")
    
    tab1, tab2, tab3 = st.tabs(["Add New Face", "View Database", "Live Add Face"])
    
    with tab1:
        st.subheader("Add New Face to Database")
        with st.form("add_face_form"):
            # Basic Information
            st.markdown("#### Basic Information")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Person Name *", help="Enter the name of the person")
                age = st.number_input("Age", min_value=0, max_value=120, value=None)
            with col2:
                occupation = st.text_input("Occupation", help="Job title or profession")
                department = st.text_input("Department", help="Department or division")
            
            description = st.text_area("Description", help="Additional information about the person")
            contact_info = st.text_input("Contact Info", help="Email, phone, or other contact details")
            
            uploaded_file = st.file_uploader(
                "Upload Face Image *",
                type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif', 'webp'],
                help="Upload a clear image of the person's face (supports JPG, PNG, BMP, TIFF, WebP)"
            )
            
            submit_button = st.form_submit_button("Add to Database")
            
            if submit_button:
                if name and uploaded_file:
                    try:
                        image = Image.open(uploaded_file)
                        
                        # Display image info for validation
                        st.info(f"Image format: {image.format}, Mode: {image.mode}, Size: {image.size}")
                        
                        # Show preview of the image
                        st.image(image, caption="Image Preview", use_container_width=True, width=200)
                        
                        success, message = face_manager.add_face_to_database(
                            name=name,
                            image=image,
                            description=description,
                            added_by=st.session_state.current_user['username'],
                            age=age if age and age > 0 else None,
                            occupation=occupation,
                            department=department,
                            contact_info=contact_info
                        )
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
                else:
                    st.error("Please provide both name and image")
    
    with tab2:
        st.subheader("Face Database")
        faces = face_manager.get_all_faces()
        
        # Check if we should show a specific profile
        if 'show_profile_id' in st.session_state and st.session_state.show_profile_id:
            face_id = st.session_state.show_profile_id
            face_name = st.session_state.get('show_profile_name', 'Unknown')
            
            # Back button
            if st.button("⬅️ Back to Face Database"):
                st.session_state.show_profile_id = None
                st.session_state.show_profile_name = None
                st.rerun()
            
            # Show detailed profile
            display_face_profile(face_id, face_name)
        
        else:
            # Normal database view
            if faces:
                st.info(f"Total faces in database: {len(faces)}")
                
                # Search functionality
                search_term = st.text_input("🔍 Search by name:", placeholder="Enter name to search...")
                
                # Filter faces based on search
                if search_term:
                    filtered_faces = [face for face in faces if search_term.lower() in face['name'].lower()]
                else:
                    filtered_faces = faces
                
                if filtered_faces:
                    st.write(f"**Showing {len(filtered_faces)} of {len(faces)} faces**")
                    
                    # Display as cards with enhanced profile information
                    for face in filtered_faces:
                        with st.expander(f"👤 {face['name']} (ID: {face['id']}) - {face.get('scan_count', 0)} scans"):
                            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                            
                            with col1:
                                st.write("**Basic Information**")
                                if face.get('age'):
                                    st.write(f"Age: {face['age']}")
                                if face.get('occupation'):
                                    st.write(f"Occupation: {face['occupation']}")
                                if face.get('department'):
                                    st.write(f"Department: {face['department']}")
                                if face.get('contact_info'):
                                    st.write(f"Contact: {face['contact_info']}")
                            
                            with col2:
                                st.write("**Scan Statistics**")
                                st.write(f"Total Scans: {face.get('scan_count', 0)}")
                                if face.get('last_seen'):
                                    st.write(f"Last Seen: {face['last_seen']}")
                                st.write(f"Added: {face['timestamp']}")
                                if face.get('added_by'):
                                    st.write(f"Added by: {face['added_by']}")
                            
                            with col3:
                                st.write("**Description**")
                                if face.get('description'):
                                    st.write(face['description'])
                                else:
                                    st.write("No description available")
                            
                            with col4:
                                st.write("**Actions**")
                                # Profile button for detailed view
                                if st.button("📊 View Profile", key=f"profile_{face['id']}", help="View detailed scan history and analytics"):
                                    st.session_state.show_profile_id = face['id']
                                    st.session_state.show_profile_name = face['name']
                                    st.rerun()
                                
                                # Show scan count as metric
                                st.metric("Scans", face.get('scan_count', 0))
                    
                    # Quick overview table with clickable names
                    st.markdown("### 📋 Quick Overview Table")
                    st.markdown("*Click on any name to view detailed profile*")
                    
                    # Create a more interactive table
                    for face in filtered_faces:
                        cols = st.columns([3, 2, 2, 2, 2, 2])
                        
                        with cols[0]:
                            # Clickable name button
                            if st.button(f"👤 {face['name']}", key=f"name_btn_{face['id']}", help="Click to view detailed profile"):
                                st.session_state.show_profile_id = face['id']
                                st.session_state.show_profile_name = face['name']
                                st.rerun()
                        
                        with cols[1]:
                            st.write(f"Age: {face.get('age', 'N/A')}")
                        
                        with cols[2]:
                            st.write(f"Dept: {face.get('department', 'N/A')}")
                        
                        with cols[3]:
                            scan_count = face.get('scan_count', 0)
                            if scan_count > 0:
                                st.success(f"Scans: {scan_count}")
                            else:
                                st.info("Scans: 0")
                        
                        with cols[4]:
                            if face.get('last_seen'):
                                st.write(f"Last: {face['last_seen'][:10]}")
                            else:
                                st.write("Never scanned")
                        
                        with cols[5]:
                            st.write(f"By: {face.get('added_by', 'Unknown')}")
                        
                        st.divider()
                
                else:
                    st.warning(f"No faces found matching '{search_term}'")
            
            else:
                st.info("No faces in database")
    
    with tab3:
        st.subheader("Live Add Face")
        st.info("📌 Use your camera to capture and add a new face to the database")
        
        # Camera input for adding faces
        camera_input = st.camera_input("Take a picture to add to database")
        
        if camera_input is not None:
            image = Image.open(camera_input)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, caption="Captured Image", use_container_width=True)
            
            with col2:
                with st.form("live_add_form"):
                    st.markdown("#### Person Details")
                    name = st.text_input("Person Name *")
                    age = st.number_input("Age", min_value=0, max_value=120, value=None)
                    occupation = st.text_input("Occupation")
                    department = st.text_input("Department")
                    contact_info = st.text_input("Contact Info")
                    description = st.text_area("Description")
                    
                    add_button = st.form_submit_button("Add to Database")
                    
                    if add_button:
                        if name:
                            try:
                                success, message = face_manager.add_face_to_database(
                                    name=name,
                                    image=image,
                                    description=description,
                                    added_by=st.session_state.current_user['username'],
                                    age=age if age and age > 0 else None,
                                    occupation=occupation,
                                    department=department,
                                    contact_info=contact_info
                                )
                                
                                if success:
                                    st.success(message)
                                    st.balloons()
                                else:
                                    st.error(message)
                            except Exception as e:
                                st.error(f"Error processing image: {str(e)}")
                        else:
                            st.error("Please provide a name for the person")

def user_profile():
    """User profile page"""
    st.subheader("👤 My Profile")
    
    user = st.session_state.current_user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {user['username']}")
        st.info(f"**User Type:** {user['user_type']}")
        st.info(f"**User ID:** {user['id']}")
    
    with col2:
        # Get user profile data
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT recognized_faces, total_recognitions, last_recognition
            FROM user_profiles WHERE user_id = ?
        ''', (user['id'],))
        
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            recognized_faces = json.loads(profile[0] or '[]')
            st.metric("Total Recognitions", profile[1] or 0)
            st.metric("Unique Faces Recognized", len(recognized_faces))
            if profile[2]:
                st.info(f"Last Recognition: {profile[2]}")
            
            if recognized_faces:
                st.subheader("Recognized People:")
                for face in recognized_faces:
                    st.write(f"• {face}")
        else:
            st.info("No recognition data available")

def user_recognition_history():
    """User's recognition history"""
    st.subheader("📊 Recognition History")
    
    user_id = st.session_state.current_user['id']
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT recognized_person, confidence, timestamp, method
        FROM recognition_logs 
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 50
    ''', (user_id,))
    
    logs = cursor.fetchall()
    conn.close()
    
    if logs:
        df = pd.DataFrame(logs, columns=['Person', 'Confidence', 'Timestamp', 'Method'])
        st.dataframe(df, use_container_width=True)
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recognitions", len(logs))
        with col2:
            avg_confidence = sum([log[1] for log in logs]) / len(logs)
            st.metric("Average Confidence", f"{avg_confidence:.2f}%")
        with col3:
            unique_people = len(set([log[0] for log in logs]))
            st.metric("Unique People", unique_people)
    else:
        st.info("No recognition history available")

def system_analytics():
    """System analytics (admin only)"""
    st.subheader("📊 System Analytics")
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Total statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM faces")
    total_faces = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recognition_logs")
    total_recognitions = cursor.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Total Faces", total_faces)
    with col3:
        st.metric("Total Recognitions", total_recognitions)
    
    # Recent activity
    st.subheader("Recent Activity")
    cursor.execute('''
        SELECT u.username, rl.recognized_person, rl.confidence, rl.timestamp, rl.method
        FROM recognition_logs rl
        JOIN users u ON rl.user_id = u.id
        ORDER BY rl.timestamp DESC
        LIMIT 20
    ''')
    
    recent_logs = cursor.fetchall()
    if recent_logs:
        df = pd.DataFrame(recent_logs, columns=['User', 'Recognized Person', 'Confidence', 'Timestamp', 'Method'])
        st.dataframe(df, use_container_width=True)
    
    conn.close()

def recognition_logs():
    """View all recognition logs (admin only)"""
    st.subheader("📋 Recognition Logs")
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.username, rl.recognized_person, rl.confidence, rl.timestamp, rl.method
        FROM recognition_logs rl
        JOIN users u ON rl.user_id = u.id
        ORDER BY rl.timestamp DESC
    ''')
    
    logs = cursor.fetchall()
    conn.close()
    
    if logs:
        df = pd.DataFrame(logs, columns=['User', 'Recognized Person', 'Confidence', 'Timestamp', 'Method'])
        st.dataframe(df, use_container_width=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"recognition_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No recognition logs available")

def user_profiles_admin():
    """View user profiles (admin only)"""
    st.subheader("👥 User Profiles")
    
    users = db_manager.get_all_users()
    
    if users:
        for user in users:
            with st.expander(f"User: {user['username']} ({user['user_type']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**User ID:** {user['id']}")
                    st.write(f"**Created:** {user['created_at']}")
                    st.write(f"**Last Login:** {user['last_login'] or 'Never'}")
                
                with col2:
                    # Get user's recognition data
                    conn = db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT COUNT(*) FROM recognition_logs WHERE user_id = ?
                    ''', (user['id'],))
                    total_recognitions = cursor.fetchone()[0]
                    
                    cursor.execute('''
                        SELECT recognized_faces, total_recognitions FROM user_profiles WHERE user_id = ?
                    ''', (user['id'],))
                    profile = cursor.fetchone()
                    
                    st.write(f"**Total Recognitions:** {total_recognitions}")
                    if profile:
                        recognized_faces = json.loads(profile[0] or '[]')
                        st.write(f"**Unique Faces:** {len(recognized_faces)}")
                    else:
                        st.write("**Unique Faces:** 0")
                    
                    conn.close()
    else:
        st.info("No users found")

def main():
    """Main application function"""
    
    # Logout button in sidebar
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.current_user = None
                st.rerun()
            
            st.markdown("---")
            st.info(f"Logged in as: **{st.session_state.current_user['username']}**")
            st.info(f"Role: **{st.session_state.current_user['user_type']}**")
    
    # Route to appropriate page based on login status
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_type == 'admin':
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()
