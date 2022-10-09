from fastapi import APIRouter, Depends
from security import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
async def healthy(db: Session = Depends(deps.get_db)):
    response = {"status": "healthy"}
    return response
