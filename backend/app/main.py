from fastapi import FastAPI, Depends, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from . import crud, models, database


models.Base.metadata.create_all(bind=database.engine)
MOCK_IMAGES_DATA = [
    {"id": "img_001", "url": "https://picsum.photos/id/1/400/300", "suggested_label": "workstation", "confidence": 0.95},
    {"id": "img_002", "url": "https://picsum.photos/id/20/400/300", "suggested_label": "desk", "confidence": 0.82},
    {"id": "img_003", "url": "https://picsum.photos/id/237/400/300", "suggested_label": "dog", "confidence": 0.88},
    {"id": "img_004", "url": "https://picsum.photos/id/40/400/300", "suggested_label": "nose", "confidence": 0.76},
    {"id": "img_005", "url": "https://picsum.photos/id/101/400/300", "suggested_label": "sky", "confidence": 0.91},
    {"id": "img_006", "url": "https://picsum.photos/id/111/400/300", "suggested_label": "car", "confidence": 0.65},
    {"id": "img_007", "url": "https://picsum.photos/id/200/400/300", "suggested_label": "landscape", "confidence": 0.79},
    {"id": "img_008", "url": "https://picsum.photos/id/219/400/300", "suggested_label": "kitten", "confidence": 0.33},
    {"id": "img_009", "url": "https://picsum.photos/id/301/400/300", "suggested_label": "road", "confidence": 0.87},
    {"id": "img_010", "url": "https://picsum.photos/id/349/400/300", "suggested_label": "city", "confidence": 0.92},
]


def populate_db_on_startup():
    db = database.SessionLocal()
    try:
        if db.query(models.Image).count() == 0:
            for img_data in MOCK_IMAGES_DATA:
                db_image = models.Image(**img_data)
                db.add(db_image)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_db_on_startup() 
    yield

# :ToDo Remove when FE also done
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/images/next", response_model=models.ImageResponse)
def get_next_image_to_review(db: Session = Depends(database.get_db)):
    image = crud.get_next_image(db)
    
    if not image:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    return image

@app.get("/api/stats", response_model=models.StatsResponse)
def get_stats(db: Session = Depends(database.get_db)):
    stats = crud.get_review_stats(db)
    return stats

@app.post(
    "/api/labels", 
    response_model=models.LabelResponse, 
    status_code=status.HTTP_201_CREATED
)
def submit_label(label_in: models.LabelRequest, db: Session = Depends(database.get_db)):
    db_label = crud.create_verified_label(
        db=db, 
        image_id=label_in.image_id, 
        label=label_in.label
    )
    return db_label

@app.delete("/api/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_label_by_id(db=db, label_id=label_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Label not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)