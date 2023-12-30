
from src.deploy.infrastructure.models import Deploy
from src.shared.domain.exeptions.in_use import ResourceInUseError


async def check_deploy_in_use(db, db_provider, account_id, cloud_provider, updated=None):
    db_deploy = (
        db.query(Deploy)
        .filter(Deploy.squad == db_provider.squad)
        .filter(Deploy.environment == db_provider.environment)
        .filter(Deploy.stack_name.like(f'{cloud_provider}%'))
        .first()
    )

    if db_deploy:
        if updated and (updated.squad != db_provider.squad or updated.environment != db_provider.environment):
            raise ResourceInUseError(account_id)
        elif not updated:
            raise ResourceInUseError(account_id)

