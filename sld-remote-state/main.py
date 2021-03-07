from fastapi import FastAPI, HTTPException
import json
from configs.store import settings

print(f'''
#####################################################################
Stack LifeCycle Deployment RemoteState  {settings.SLD_RM_VER}       #
#####################################################################

------------------------------------------------
remote state = {settings.SLD_STORE}            
------------------------------------------------
''')

if settings.SLD_STORE == "S3":
    from stores.bucket_s3 import S3Store as Store
if settings.SLD_STORE == "local":
    from stores.local import LocalStore as Store



remote_state = Store('.remote_states')
app = FastAPI(title=f"RemoteState Stack Lifecycle Deployment {settings.SLD_RM_VER} ", version=f"{settings.SLD_RM_VER}",
              description="ARM - API RemoteState Mapping - Remote State for many backends, analogous to an ORM")


tags_metadata = [
    {
        "name": "Remote-state",
        "description": "ARM - API RemoteState MAPPING - Remote State for many backends, analogous to an ORM",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://sld.io/",
        },
    }
]

@app.get('/', tags=["Remote_state"])
async def health():
    return {"status": "healthy"}


@app.get('/terraform_state/{id}', tags=["Remote_state"] )
async def get_tfstate(id: str):
    s = remote_state.get(id)
    if not s:
        raise HTTPException(status_code=404)
    return s


@app.post('/terraform_state/{id}', tags=["Remote_state"])
async def post_tfstate(id: str, tfstate: dict):
    json.dumps(remote_state.put(id, tfstate))
    return {}


@app.put('/terraform_lock/{id}', tags=["Remote_state"])
async def put_tfstate(id: str, tfstate: dict):
    success, info = remote_state.lock(id, tfstate)
    if not success:
        raise HTTPException(status_code=423)
    return info


@app.delete('/terraform_lock/{id}', tags=["Remote_state"])
async def delete_tfstate(id: str):
    tfstate = {}
    if not remote_state.unlock(id, tfstate):
        raise HTTPException(status_code=404)
    return {}
