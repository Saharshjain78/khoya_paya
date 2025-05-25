import React, { useState, useRef } from 'react';

const Camera = () => {
    const [imageSrc, setImageSrc] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    const startCamera = () => {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
            })
            .catch(err => {
                console.error("Error accessing the camera: ", err);
            });
    };

    const captureImage = () => {
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/png');
        setImageSrc(imageData);
        // Here you can add functionality to send the imageData to the backend for face recognition
    };

    return (
        <div>
            <h2>Camera</h2>
            <video ref={videoRef} width="640" height="480" />
            <button onClick={startCamera}>Start Camera</button>
            <button onClick={captureImage}>Capture Image</button>
            <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />
            {imageSrc && <img src={imageSrc} alt="Captured" />}
        </div>
    );
};

export default Camera;