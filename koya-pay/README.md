# Koya Pay

Koya Pay is a comprehensive application designed for face recognition and database management. The application leverages modern web technologies, including JavaScript and HTML for the frontend, and Python with Flask for the backend. This document provides an overview of the project structure, features, and setup instructions.

## Project Structure

The project is organized into two main directories: `frontend` and `backend`.

### Frontend

- **public/**: Contains static files.
  - `index.html`: The main entry point for the frontend application.
  - `manifest.json`: Metadata for Progressive Web App (PWA) capabilities.

- **src/**: Contains the source code for the React application.
  - **assets/**: Contains styles and other assets.
    - `styles/main.css`: Main styles for the application.
  - **components/**: Contains React components.
    - `App.js`: Root component managing layout and routing.
    - `Camera.js`: Handles camera functionality for image capture.
    - `Database.js`: Interface for interacting with the database.
    - `FaceMatch.js`: Displays results of face recognition.
    - `Header.js`: Renders the application header.
    - `LocationUpdate.js`: Prompts user to update location of matched photos.
    - `PhotoUpload.js`: Allows users to upload photos for processing.
  - **services/**: Contains service functions for API calls and face recognition.
    - `api.js`: Functions for making API calls to the backend.
    - `faceRecognition.js`: Functions related to face recognition logic.
  - `index.js`: Entry point for the React application.

- `package.json`: Configuration file for npm, listing dependencies and scripts.

### Backend

- **app.py**: Main entry point for the backend application, setting up the Flask server.
- **config.py**: Configuration settings for the backend application.
- **models/**: Contains database model definitions.
  - `database.py`: ORM setup for managing data.
  - `face_model.py`: Model for storing face recognition data.
- **routes/**: Contains route definitions for the application.
  - `auth.py`: Handles authentication routes.
  - `database.py`: Routes for database interactions.
  - `recognition.py`: Routes for face recognition functionality.
- **services/**: Contains business logic for the application.
  - `face_recognition.py`: Logic for face recognition.
  - `location_service.py`: Handles location-related functionalities.
- **utils/**: Contains utility functions for the application.
  - `image_processing.py`: Utility functions for image processing.
- `requirements.txt`: Lists Python dependencies required for the backend.

## Features

- **Face Recognition**: Users can capture images using the camera or upload photos for face recognition.
- **Database Management**: Users can view, add, and manage entries in the database.
- **Location Update**: When a face match is found, users are prompted to update the location of the matched photo.
- **Responsive Design**: The application is designed to be responsive and user-friendly across devices.

## Setup Instructions

### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies using npm:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

### Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the Flask application:
   ```
   python app.py
   ```

## Conclusion

Koya Pay is a powerful application that combines face recognition technology with a user-friendly interface for database management. With its modular architecture and clear separation of concerns, it is designed for scalability and ease of maintenance.