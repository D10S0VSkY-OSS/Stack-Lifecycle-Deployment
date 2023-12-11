import re
from collections import defaultdict

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.deploy.infrastructure import repositories as crud_deploys
from src.shared.helpers.get_data import check_squad_user
from src.shared.security import deps
from src.stacks.infrastructure import repositories as crud_stacks
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


class MetadataProcessor:
    def __init__(self, data):
        self.data = data
        self.grouped_metadata = defaultdict(
            lambda: {"vars_group": "", "descriptions": []}
        )

    def add_metadata(self):
        for key, value in self.data.items():
            original_description = value.get("description")
            metadata = self._parse_description(original_description)
            if metadata is not None and "_no_metadata" in metadata:
                continue
            self._group_metadata(metadata)

            if metadata is None or "error" in metadata:
                value["metadata"] = {
                    "error": "Description format is incorrect or missing required fields."
                }
            else:
                value["description"] = original_description
                if "description_cleaned" in metadata:
                    metadata["description"] = metadata.pop("description_cleaned")
                value["metadata"] = metadata

        self._update_group_descriptions()

        return self.data

    def _parse_description(self, description):
        # Asegurarse de que description sea una cadena de texto
        description = str(description)
        
        key_values = dict(re.findall(r"(\w+): ([^\n]*)", description))
        
        if all(key in key_values for key in ["order", "vars_group"]):
            return self._process_newline_format(key_values)
    
        if "|" not in description:
            return {"_no_metadata": "Basic configuration"}
    
        if description.count("|") >= 2:
            return self._process_pipe_format(description)
    
        return {"error": "Invalid format"}

    def _process_pipe_format(self, description):
        parts = [part.strip() for part in description.split("|")]
        if parts[0]:
            group_key = (
                re.match(r"([A-Za-z])\d*", parts[0]).group(1) if parts[0] else ""
            )
            return {
                "order": parts[0],
                "vars_group": parts[1]
                if parts[1]
                else self.grouped_metadata[group_key]["vars_group"],
                "description_cleaned": parts[2] if len(parts) > 2 else "",
                "parameter_type": "pipe",
            }
        return {"error": "Invalid pipe format"}

    def _process_newline_format(self, key_values):
        metadata = {k: v.strip('"') for k, v in key_values.items()}
        if "query_type" in metadata and "query" in metadata and "query_key" in metadata:
            metadata["parameter_type"] = "QueryParams"
        else:
            metadata["parameter_type"] = "EOF"
        metadata["description"] = metadata.pop("description", "").strip("\"'")
        return metadata

    def _group_metadata(self, metadata):
        if "order" in metadata and not metadata.get("error"):
            group_key = re.match(r"([A-Za-z])\d*", metadata["order"]).group(1)
            if not self.grouped_metadata[group_key]["vars_group"]:
                self.grouped_metadata[group_key]["vars_group"] = metadata.get(
                    "vars_group", ""
                )
            self.grouped_metadata[group_key]["descriptions"].append(
                metadata.get("description", "")
            )

    def _update_group_descriptions(self):
        for key, group in self.grouped_metadata.items():
            group["description"] = "\n".join(group["descriptions"])


async def get_json(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Pass the name of the stack or the id, and I will return the variables supported by the stack as json format
    """
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            if result is None:
                raise HTTPException(
                    status_code=404, detail="Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            metadata_result = MetadataProcessor(result.var_json.get("variable"))
            return metadata_result.add_metadata()
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result is None:
                raise HTTPException(
                    status_code=404, detail="Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail="Not enough permissions"
                        )
            metadata_result = MetadataProcessor(result.var_json.get("variable"))
            return metadata_result.add_metadata()
    except Exception as err:
        raise err


async def get_list(
    stack,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """
    Pass the name of the stack or the id, and I will return the variables supported by the stack as list format
    """
    try:
        if stack.isdigit():
            result = crud_stacks.get_stack_by_id(db=db, stack_id=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_list
        else:
            result = crud_stacks.get_stack_by_name(db=db, stack_name=stack)
            if result == None:
                raise HTTPException(
                    status_code=404, detail=f"Not found"
                )
            if not crud_users.is_master(db, current_user):
                if "*" not in result.squad_access:
                    if not check_squad_user(current_user.squad, result.squad_access):
                        raise HTTPException(
                            status_code=403, detail=f"Not enough permissions"
                        )
            return result.var_list
    except Exception as err:
        raise err


async def get_deploy_by_id(
    deploy_id: int,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):

    try:
        result = crud_deploys.get_deploy_by_id(db=db, deploy_id=deploy_id)
        if result == None:
            raise HTTPException(
                status_code=404, detail=f"Not found"
            )
        if not crud_users.is_master(db, current_user):
            if not check_squad_user(current_user.squad, [result.squad]):
                raise HTTPException(
                    status_code=403, detail=f"Not enough permissions"
                )
        return result.variables
    except Exception as err:
        raise err
