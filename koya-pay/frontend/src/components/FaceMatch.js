import React, { useState, useEffect } from 'react';
import { fetchFaceMatches } from '../services/faceRecognition';

const FaceMatch = () => {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getFaceMatches = async () => {
            try {
                const data = await fetchFaceMatches();
                setMatches(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        getFaceMatches();
    }, []);

    const handleLocationUpdate = (matchId) => {
        // Logic to update location for the matched face
        // This could involve navigating to a LocationUpdate component or opening a modal
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <h2>Face Match Results</h2>
            {matches.length === 0 ? (
                <p>No matches found.</p>
            ) : (
                <ul>
                    {matches.map((match) => (
                        <li key={match.id}>
                            <img src={match.photoUrl} alt={match.name} />
                            <p>Name: {match.name}</p>
                            <p>Location: {match.location}</p>
                            <button onClick={() => handleLocationUpdate(match.id)}>Update Location</button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default FaceMatch;