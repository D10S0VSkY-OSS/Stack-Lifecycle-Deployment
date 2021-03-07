from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from security import deps

router = APIRouter()


@router.get("/")
async def healthy(db: Session = Depends(deps.get_db)):
    response = {"status": "healthy"}
    return response
