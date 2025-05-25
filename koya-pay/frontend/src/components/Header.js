import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
    return (
        <header className="header">
            <h1 className="header-title">Koya Pay</h1>
            <nav className="header-nav">
                <ul>
                    <li>
                        <Link to="/">Home</Link>
                    </li>
                    <li>
                        <Link to="/database">Database</Link>
                    </li>
                    <li>
                        <Link to="/photo-upload">Upload Photo</Link>
                    </li>
                    <li>
                        <Link to="/camera">Camera</Link>
                    </li>
                    <li>
                        <Link to="/face-match">Face Match</Link>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;