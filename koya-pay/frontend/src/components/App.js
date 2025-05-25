import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Header from './Header';
import Camera from './Camera';
import Database from './Database';
import FaceMatch from './FaceMatch';
import LocationUpdate from './LocationUpdate';
import PhotoUpload from './PhotoUpload';
import './assets/styles/main.css';

const App = () => {
    return (
        <Router>
            <div className="App">
                <Header />
                <Switch>
                    <Route path="/" exact component={PhotoUpload} />
                    <Route path="/camera" component={Camera} />
                    <Route path="/database" component={Database} />
                    <Route path="/face-match" component={FaceMatch} />
                    <Route path="/location-update" component={LocationUpdate} />
                </Switch>
            </div>
        </Router>
    );
};

export default App;