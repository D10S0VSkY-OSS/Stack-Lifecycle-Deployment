from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.shared.helpers.get_data import check_providers, check_squad_stack
from src.shared.helpers.push_task import sync_git
from src.shared.security import deps
from src.stacks.domain.entities import stacks as schemas_stacks
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.domain.entities import users as schemas_users

router = APIRouter()


def create_new_stack(
    stack: schemas_stacks.StackCreate,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    name = "default"
    environment = "default"
    squad = "squad"
    branch = stack.branch

    # Checkif stack name providers are supperted
    check_providers(stack_name=stack.stack_name)
    # Check if stack exist
    db_stack = crud_stacks.get_stack_by_name(db, stack_name=stack.stack_name)
    if db_stack:
        raise HTTPException(status_code=409, detail="The stack name already exist")
    # Check if the user have permissions for create stack
    check_squad_stack(db, current_user, current_user.squad, stack.squad_access)
    # Push git task to queue squad, all workers are subscribed to this queue
    task = sync_git(
        stack_name=stack.stack_name,
        git_repo=stack.git_repo,
        branch=branch,
        project_path=stack.project_path,
        environment=environment,
        squad=squad,
        name=name,
    )
    variables_list = [i for i in task[1]["variable"].keys()]
    try:
        # pesrsist data in db
        result = crud_stacks.create_new_stack(
            db=db,
            stack=stack,
            user_id=current_user.id,
            username=current_user.username,
            task_id=task[0],
            var_json=task[1],
            var_list=variables_list,
            squad_access=stack.squad_access,
        )

        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Create Stack {stack.stack_name}",
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=409, detail=f"Duplicate entry {err}")
