# Khoya Paya - Face Recognition System

A modern Streamlit-based face recognition application for identifying people using advanced facial recognition technology.

## Quick Start

### Prerequisites
- Python 3.7+
- Webcam (optional, for live recognition)

### Installation & Running

1. **Clone/Download the project**
   ```bash
   cd khoya_paya
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```
   Or use the provided startup scripts:
   - Windows: `start_app.bat`
   - PowerShell: `start_app.ps1`

5. **Access the app**
   Open your browser and go to: `http://localhost:8501`

## Features

- 🔐 **User Authentication**: Secure login system with admin and user roles
- 📸 **Photo Recognition**: Upload images to identify faces
- 📹 **Live Camera Recognition**: Real-time face recognition via webcam
- 👤 **Profile Management**: Detailed person profiles with contact info
- 📊 **Recognition History**: Track all recognition events
- 🗄️ **Database Management**: Add, edit, and manage face database
- 📈 **Analytics Dashboard**: Recognition statistics and insights

## Project Structure

```
khoya_paya/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── start_app.bat          # Windows startup script
├── start_app.ps1          # PowerShell startup script
├── database/              # SQLite databases
├── known_faces/           # Face data storage
├── user_profiles/         # User profile data
├── photos/                # Sample photos
└── README.md              # This file
```

## Usage

### Default Login Credentials
- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

### Adding New Faces
1. Login as admin
2. Go to "Face Database Management"
3. Use camera or upload photo
4. Fill in person details
5. Save to database

### Recognition
1. Login as user or admin
2. Choose "Photo Recognition" or "Live Recognition"
3. Upload image or use camera
4. View recognition results and person profile

## Technical Details

- **Backend**: Streamlit + SQLite
- **Face Recognition**: face_recognition library (dlib-based)
- **Image Processing**: OpenCV + Pillow
- **Database**: SQLite with comprehensive schema
- **Frontend**: Streamlit components with custom styling

## Troubleshooting

1. **Face recognition not working**: Ensure good lighting and clear face visibility
2. **Camera issues**: Check webcam permissions and availability
3. **Installation problems**: Try installing cmake before face_recognition
4. **Performance**: Reduce image size for faster processing

## Dependencies

- streamlit>=1.28.0
- opencv-python-headless==4.8.1.78
- Pillow>=9.0.0
- numpy>=1.21.0
- pandas>=1.5.0
- face_recognition>=1.3.0
