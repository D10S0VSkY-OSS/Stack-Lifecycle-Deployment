from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.shared.security import deps

router = APIRouter()


@router.get("/")
async def healthy(db: Session = Depends(deps.get_db)):
    response = {"status": "healthy"}
    return response
