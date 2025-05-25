from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FaceModel(Base):
    __tablename__ = 'faces'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    location = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)

    def __repr__(self):
        return f"<FaceModel(id={self.id}, name={self.name}, location={self.location}, confidence_score={self.confidence_score})>"