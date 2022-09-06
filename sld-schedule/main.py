from fastapi import FastAPI
from helpers.get_deploy_schedule import (addDeployToSchedule, getJob, getJobs,
                                         init_check_schedule, removeJob)

app = FastAPI(
    title="Schedule Stack Lifecycle Deployment 1.0.0-RC",
    version="1.0.0-RC",
    description="Schedule api for automatic execution at specific intervals same as cron",
)

init_check_schedule()


@app.get("/")
async def health():
    return {"status": "healthy"}


@app.get("/schedules/")
async def get_schedule():
    return {"result": str(getJobs())}


@app.get("/schedule/{id}")
async def get_schedule(id: str):
    result = getJob(id)
    return {"deploy": str(result[0]), "destroy": str(result[1])}


@app.post("/schedule/{id}")
async def add_schedule_by_deploy_id(id: str):
    try:
        result = addDeployToSchedule(id)
    except Exception as err:
        result = [err, err]
    return {"deploy": str(result[0]), "destroy": str(result[1])}


@app.delete("/schedule/{id}")
async def delete_tfstate(id: str):
    return {"result": str(removeJob(id))}
