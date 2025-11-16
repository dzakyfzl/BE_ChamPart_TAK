from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from .database.database import get_db
from .database.database import Base, engine

from .database.models.bakat import Bakat



app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def get_all_bakat(db: Session = Depends(get_db)):
    try:
        bakat_list = db.query(Bakat).all()
        return {
            "status": "success",
            "data": [
                {
                    "idBakat": bakat.idBakat,
                    "nama": bakat.nama
                } 
                for bakat in bakat_list
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}