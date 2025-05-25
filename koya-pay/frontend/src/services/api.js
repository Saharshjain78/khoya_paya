import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api'; // Adjust the base URL as needed

// Function to upload a photo for face recognition
export const uploadPhoto = async (formData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading photo:', error);
        throw error;
    }
};

// Function to get database entries
export const getDatabaseEntries = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/database`);
        return response.data;
    } catch (error) {
        console.error('Error fetching database entries:', error);
        throw error;
    }
};

// Function to update location of a matched photo
export const updateLocation = async (photoId, locationData) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/location/${photoId}`, locationData);
        return response.data;
    } catch (error) {
        console.error('Error updating location:', error);
        throw error;
    }
};

// Function to match a face from the uploaded photo
export const matchFace = async (formData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/match`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error matching face:', error);
        throw error;
    }
};