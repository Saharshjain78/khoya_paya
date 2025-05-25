from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    photo_path = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'

class FaceRecognition(db.Model):
    __tablename__ = 'face_recognition'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    face_data = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('faces', lazy=True))

    def __repr__(self):
        return f'<FaceRecognition {self.id} for User {self.user_id}>'