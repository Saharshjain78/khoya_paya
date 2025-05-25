# Khoya Paya - Missing Person Finder

Khoya Paya is a comprehensive face recognition system designed to help locate missing persons by leveraging facial recognition technology. The application consists of a Python-based recognition system and a web application with React frontend and Flask backend.

## Project Overview

This project aims to address the challenge of locating missing persons by creating a centralized system where photographs can be uploaded, stored, and matched against images of known missing individuals. The system uses advanced facial recognition algorithms to identify potential matches.

## Repository Structure

### Root Directory (Legacy Python Scripts)
- `add_image_gui.py`: GUI tool for adding images to the database
- `add_image.py`: Script for adding images to the database
- `database_creator.py`: Script for initializing the database
- `database_viewer.py`: Script for viewing database contents
- `live_recognition_direct.py`, `live_recognition_fixed.py`, `live_recognition_improved.py`, `live_recognition.py`: Various implementations of live facial recognition
- `program.py`: Main program entry point
- `verify_database.py`: Script for verifying database integrity

### Koya Pay (Web Application)

#### Frontend
- React-based user interface for interacting with the system
- Components for camera access, photo uploads, and viewing results
- Services for API communication and face recognition

#### Backend
- Flask-based REST API
- Face recognition services
- Database models and interactions
- Location tracking services

## Features

- **Face Recognition**: Detect and match faces against a database of missing persons
- **Database Management**: Add, view, and manage entries in the missing persons database
- **Live Recognition**: Process real-time video feeds to identify matches
- **Location Tracking**: Update and track locations when matches are found
- **User-friendly Interface**: Both standalone Python application and web interface

## Setup Instructions

### Prerequisites
- Python 3.7+
- Node.js and npm
- Git

### Python Environment Setup
1. Clone the repository
2. Install required Python packages:
```
pip install -r requirements.txt
```

### Web Application Setup
1. Navigate to the `koya-pay/backend` directory
2. Install backend dependencies:
```
pip install -r requirements.txt
```
3. Navigate to the `koya-pay/frontend` directory
4. Install frontend dependencies:
```
npm install
```

## Usage

### Python Scripts
- Run `program.py` to start the main application
- Use `add_image_gui.py` to add new faces to the database
- Use `database_viewer.py` to view the current database entries

### Web Application
1. Start the backend server:
```
cd koya-pay/backend
python app.py
```
2. Start the frontend development server:
```
cd koya-pay/frontend
npm start
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
