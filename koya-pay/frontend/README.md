# Koya Pay Frontend Documentation

## Overview
Koya Pay is a web application designed for face recognition and database management. The frontend is built using React, HTML, and CSS, providing a user-friendly interface for interacting with the backend services.

## Features
- **Camera Functionality**: Users can capture images directly from their device's camera for face recognition.
- **Photo Upload**: Users can upload photos from their device for processing.
- **Database Management**: An interface for viewing and managing database entries.
- **Face Recognition**: Scans uploaded images and matches them with faces stored in the database.
- **Location Update**: Prompts users to update the location of matched photos.

## Project Structure
The frontend project is organized as follows:

```
frontend/
├── public/
│   ├── index.html          # Main HTML file
│   └── manifest.json       # PWA metadata
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css    # Main styles
│   ├── components/          # React components
│   │   ├── App.js
│   │   ├── Camera.js
│   │   ├── Database.js
│   │   ├── FaceMatch.js
│   │   ├── Header.js
│   │   ├── LocationUpdate.js
│   │   └── PhotoUpload.js
│   ├── services/            # API and face recognition services
│   │   ├── api.js
│   │   └── faceRecognition.js
│   └── index.js            # Entry point for the React application
├── package.json             # npm configuration
└── README.md                # Frontend documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the frontend directory:
   ```
   cd koya-pay/frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```

## Running the Application
To start the development server, run:
```
npm start
```
The application will be available at `http://localhost:3000`.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.