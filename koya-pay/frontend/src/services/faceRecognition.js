import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Adjust the URL as needed

export const uploadPhoto = async (photo) => {
    const formData = new FormData();
    formData.append('photo', photo);

    try {
        const response = await axios.post(`${API_URL}/upload`, formData, {
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

export const recognizeFace = async (photo) => {
    const formData = new FormData();
    formData.append('photo', photo);

    try {
        const response = await axios.post(`${API_URL}/recognize`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error recognizing face:', error);
        throw error;
    }
};

export const updateLocation = async (faceId, location) => {
    try {
        const response = await axios.put(`${API_URL}/update-location`, {
            faceId,
            location,
        });
        return response.data;
    } catch (error) {
        console.error('Error updating location:', error);
        throw error;
    }
};