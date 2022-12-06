from fastapi import APIRouter, Depends
from src.aws.domain.entities import aws as schemas_aws
from src.aws.api.container import create,get,delete

router = APIRouter()


@router.post("/", status_code=200)
async def create_new_aws_profile(
    create_aws_profile: schemas_aws.AwsAsumeProfile = Depends(create.create_new_aws_profile),
):
    return create_aws_profile


@router.get("/")
async def get_all_aws_accounts(
    get_aws_profile: schemas_aws.AwsAsumeProfile = Depends(get.get_all_aws_accounts),
):
    return get_aws_profile


@router.delete("/{aws_account_id}")
async def delete_aws_account_by_id(
    delete_aws_profile: schemas_aws.AwsAsumeProfile = Depends(delete.aws_account_by_id),
):
    return delete_aws_profile
