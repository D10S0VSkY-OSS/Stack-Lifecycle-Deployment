from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.shared.helpers.get_data import deploy, deploy_squad
from src.shared.helpers.push_task import async_schedule_delete
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def delete_schedule(
    deploy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
):
    # Get info from deploy data
    if crud_users.is_master(db, current_user):
        deploy_data = deploy(db, deploy_id=deploy_id)
        squad = deploy_data.squad
    else:
        # Get squad from current user
        squad = current_user.squad
        deploy_data = deploy_squad(db, deploy_id=deploy_id, squad=squad)
    deploy_name = deploy_data.id
    try:
        return {"task_id": async_schedule_delete(deploy_name=deploy_name, squad=squad)}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"{err}")
