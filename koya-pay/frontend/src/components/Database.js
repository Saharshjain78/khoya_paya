import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Database = () => {
    const [entries, setEntries] = useState([]);
    const [newEntry, setNewEntry] = useState('');

    useEffect(() => {
        fetchEntries();
    }, []);

    const fetchEntries = async () => {
        try {
            const response = await axios.get('/api/database');
            setEntries(response.data);
        } catch (error) {
            console.error('Error fetching entries:', error);
        }
    };

    const handleAddEntry = async () => {
        if (!newEntry) return;

        try {
            await axios.post('/api/database', { entry: newEntry });
            setNewEntry('');
            fetchEntries();
        } catch (error) {
            console.error('Error adding entry:', error);
        }
    };

    return (
        <div>
            <h2>Database Entries</h2>
            <input
                type="text"
                value={newEntry}
                onChange={(e) => setNewEntry(e.target.value)}
                placeholder="Add new entry"
            />
            <button onClick={handleAddEntry}>Add Entry</button>
            <ul>
                {entries.map((entry, index) => (
                    <li key={index}>{entry}</li>
                ))}
            </ul>
        </div>
    );
};

export default Database;