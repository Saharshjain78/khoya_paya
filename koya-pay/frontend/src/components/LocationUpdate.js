import React, { useState } from 'react';

const LocationUpdate = ({ matchedPhoto, onUpdateLocation }) => {
    const [location, setLocation] = useState('');

    const handleLocationChange = (e) => {
        setLocation(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (location) {
            onUpdateLocation(matchedPhoto.id, location);
            setLocation('');
        } else {
            alert('Please enter a location.');
        }
    };

    return (
        <div className="location-update">
            <h2>Update Location for Matched Photo</h2>
            <img src={matchedPhoto.url} alt="Matched" />
            <form onSubmit={handleSubmit}>
                <label htmlFor="location">New Location:</label>
                <input
                    type="text"
                    id="location"
                    value={location}
                    onChange={handleLocationChange}
                    placeholder="Enter new location"
                />
                <button type="submit">Update Location</button>
            </form>
        </div>
    );
};

export default LocationUpdate;