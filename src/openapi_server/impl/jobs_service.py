import asyncio
from uuid import uuid4

JOBS = {}

async def start_job():
    job_id = str(uuid4())
    JOBS[job_id] = {"status": "pending"}
    asyncio.create_task(_complete_job(job_id))
    return job_id

async def _complete_job(job_id):
    await asyncio.sleep(3)
    JOBS[job_id] = {"status": "done", "result": "Job completed successfully"}

async def get_job_status(job_id):
    return JOBS.get(job_id, {"status": "not_found"})
