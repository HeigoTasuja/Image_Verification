from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean
from pydantic import BaseModel
from .database import Base


class Image(Base):
    """Persistent representation of an image to be reviewed.

    Attributes:
        id: Primary key (string). External ID for the image.
        url: Location of the image file.
        suggested_label: Label suggested by the model.
        confidence: Model confidence score for the suggestion.
    """
    __tablename__ = "images"
    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    suggested_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)


class VerifiedLabel(Base):
    """Represents a reviewer-verified label for an image.

    Attributes:
        id: Auto-incrementing primary key.
        image_id: Foreign key to the `images.id` column.
        label: The label supplied by a human reviewer.
        was_correct: Bool indicating whether the reviewer's label matched
            the model's suggestion.
    """
    __tablename__ = "verified_labels"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(String, ForeignKey("images.id"))
    label = Column(String, nullable=False)
    was_correct = Column(Boolean, nullable=False, default=False)


class ImageResponse(BaseModel):
    """Pydantic model returned by the `/api/images/next` endpoint.

    Fields mirror the public representation of an Image used by the UI.
    """
    id: str
    url: str
    suggested_label: str
    confidence: float

    class Config:
        from_attributes = True 


class LabelRequest(BaseModel):
    """Pydantic model accepted by the `/api/labels` POST endpoint."""
    image_id: str
    label: str


class StatsResponse(BaseModel):
    """Response model for `/api/stats` summarizing review progress."""
    total_processed: int
    correct_predictions: int
    accuracy: float


class LabelResponse(BaseModel):
    """Response model returned after successfully creating a label."""
    id: int
    image_id: str
    label: str

    class Config:
        from_attributes = True