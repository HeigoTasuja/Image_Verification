from sqlalchemy import Column, Float, Integer, String, ForeignKey
from pydantic import BaseModel
from .database import Base


class Image(Base):
    __tablename__ = "images"
    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    suggested_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

class VerifiedLabel(Base):
    __tablename__ = "verified_labels"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(String, ForeignKey("images.id"))
    label = Column(String, nullable=False)


class ImageResponse(BaseModel):
    id: str
    url: str
    suggested_label: str
    confidence: float

    class Config:
        from_attributes = True 

class LabelRequest(BaseModel):
    image_id: str
    label: str