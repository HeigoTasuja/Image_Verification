from sqlalchemy.orm import Session
from . import models


def get_next_image(db: Session):
    """Return the next Image that has not yet been labelled.

    The current implementation performs an outer join between `Image` and
    `VerifiedLabel` and returns the first image that has no matching
    verified label.

    Args:
        db: SQLAlchemy Session instance.

    Returns:
        The first ``models.Image`` instance without a corresponding
        ``models.VerifiedLabel``, or ``None`` if all images have been labelled.
    """
    return (
        db.query(models.Image)
        .outerjoin(
            models.VerifiedLabel, models.Image.id == models.VerifiedLabel.image_id
        )
        .filter(models.VerifiedLabel.id == None)
        .first()
    )


def create_verified_label(db: Session, image_id: str, label: str):
    """Create and persist a VerifiedLabel for the given image.

    The function determines whether the provided ``label`` matches the
    image's ``suggested_label`` and sets ``was_correct`` accordingly.

    Args:
        db: SQLAlchemy Session instance.
        image_id: Identifier of the image being labelled.
        label: The label provided by the reviewer.

    Returns:
        The newly created ``models.VerifiedLabel`` instance (refreshed from
        the database).
    """
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
    """Compute basic review statistics.

    Returns a simple dict containing the total number of processed labels,
    how many were correct and the accuracy percentage. Accuracy is returned
    as a float in the range ``0.0`` to ``100.0``.

    Args:
        db: SQLAlchemy Session instance.

    Returns:
        A dict with keys: ``total_processed``, ``correct_predictions``, and
        ``accuracy``.
    """
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


def delete_label_by_id(db: Session, label_id: int):
    """Delete a verified label by its primary key.

    Args:
        db: SQLAlchemy Session instance.
        label_id: Primary key (int) of the VerifiedLabel to delete.

    Returns:
        True if the label existed and was deleted, False otherwise.
    """
    db_label = db.query(models.VerifiedLabel).filter(models.VerifiedLabel.id == label_id).first()
    
    if not db_label:
        return False
    db.delete(db_label)
    db.commit()    
    return True