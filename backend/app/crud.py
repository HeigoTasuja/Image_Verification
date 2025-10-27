from sqlalchemy.orm import Session
from . import models

def get_next_image(db: Session):
    return (
        db.query(models.Image)
        .outerjoin(
            models.VerifiedLabel, models.Image.id == models.VerifiedLabel.image_id
        )
        .filter(models.VerifiedLabel.id == None)
        .first()
    )

def create_verified_label(db: Session, image_id: str, label: str):
    db_label = models.VerifiedLabel(image_id=image_id, label=label)
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label