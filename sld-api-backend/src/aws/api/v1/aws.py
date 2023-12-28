from fastapi import APIRouter, Depends

from src.aws.api.container import create, delete, get, update
from src.aws.domain.entities import aws as schemas_aws

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_aws_account(
    create_aws_profile: schemas_aws.AwsAsumeProfile = Depends(
        create.create_new_aws_profile
    ),
):
    return create_aws_profile


@router.patch("/{aws_account_id}", status_code=200)
async def update_aws_account(
        update_account: schemas_aws.AwsAsumeProfile = Depends(
            update.update_aws_account
        ),
):
    return update_account


@router.get("/", status_code=200, response_model=list[schemas_aws.AwsAccountResponse])
async def get_all_aws_accounts(
    get_aws_profile: schemas_aws.AwsAccountResponse = Depends(get.get_all_aws_accounts),
):
    return get_aws_profile


@router.delete("/{aws_account_id}")
async def delete_aws_account_by_id(
    delete_aws_profile: schemas_aws.AwsAsumeProfile = Depends(delete.aws_account_by_id),
):
    return delete_aws_profile
