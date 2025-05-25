# Koya Pay Backend Documentation

## Overview
Koya Pay is a web application designed for face recognition and location tracking. The backend is built using Python with Flask, providing a robust API for the frontend to interact with. This document outlines the structure, setup, and functionality of the backend components.

## Project Structure
The backend is organized into several key directories and files:

- **app.py**: The main entry point for the Flask application, responsible for initializing the server and routing.
- **config.py**: Contains configuration settings such as database connection details and environment variables.
- **models/**: This directory includes the database models and ORM setup.
  - **database.py**: Defines the database model for managing data.
  - **face_model.py**: Defines the model for storing face recognition data and associated metadata.
- **routes/**: Contains the API routes for handling requests.
  - **auth.py**: Manages authentication routes (login, registration).
  - **database.py**: Provides routes for database interactions (adding and retrieving entries).
  - **recognition.py**: Handles face recognition functionality (processing images and returning results).
- **services/**: Contains business logic and services used by the routes.
  - **face_recognition.py**: Implements face recognition logic, including model loading and image processing.
  - **location_service.py**: Manages location-related functionalities (updating and retrieving location data).
- **utils/**: Contains utility functions for various tasks.
  - **image_processing.py**: Provides functions for image processing (resizing, format conversion).
- **requirements.txt**: Lists the Python dependencies required for the backend application.

## Setup Instructions
1. **Clone the Repository**: 
   ```
   git clone <repository-url>
   cd koya-pay/backend
   ```

2. **Create a Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```
   python app.py
   ```

## API Endpoints
- **Authentication**:
  - `POST /auth/login`: User login.
  - `POST /auth/register`: User registration.

- **Database Operations**:
  - `GET /database`: Retrieve all entries.
  - `POST /database`: Add a new entry.

- **Face Recognition**:
  - `POST /recognition`: Upload an image for face recognition and receive match results.

## Important Features
- **Face Recognition**: Utilizes advanced algorithms to match faces from uploaded images against the database.
- **Location Tracking**: Allows users to update the location of matched photos, enhancing the application's utility.
- **Database Management**: Provides a simple interface for adding and retrieving entries, ensuring data integrity and ease of use.

## Conclusion
The Koya Pay backend is designed to be scalable and efficient, providing essential services for the face recognition application. For further development, consider implementing additional features such as user roles, enhanced security measures, and performance optimizations.