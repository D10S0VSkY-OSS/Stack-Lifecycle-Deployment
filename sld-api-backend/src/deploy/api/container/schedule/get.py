from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import check_squad_user, deploy
from src.shared.helpers.push_task import async_schedule_get, async_schedule_list
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def list_schedules(
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    squad = current_user.squad
    try:
        return {"task_id": async_schedule_list(squad=squad)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")


async def get_schedule(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    deploy_data = deploy(db, deploy_id=deploy_id)
    squad = deploy_data.squad
    deploy_name = deploy_data.id
    if not crud_users.is_master(db, current_user):
        if not check_squad_user(current_user.squad, [squad]):
            raise HTTPException(
                status_code=403, detail=f"Not enough permissions in {squad}"
            )
    try:
        return {"task_id": async_schedule_get(deploy_name=deploy_name, squad=squad)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
