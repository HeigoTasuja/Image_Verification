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
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    is_correct = False
    if image and image.suggested_label == label:
        is_correct = True
    db_label = models.VerifiedLabel(
        image_id=image_id,
        label=label,
        was_correct=is_correct
    )

    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label


def get_review_stats(db: Session):
    total_processed = db.query(models.VerifiedLabel).count()
    total_correct = (
        db.query(models.VerifiedLabel)
        .filter(models.VerifiedLabel.was_correct == True)
        .count()
    )

    accuracy = 0.0
    if total_processed > 0:
        accuracy = (total_correct / total_processed) * 100
    return {
        "total_processed": total_processed,
        "correct_predictions": total_correct,
        "accuracy": accuracy
    }