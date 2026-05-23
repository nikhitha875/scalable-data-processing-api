from fastapi import FastAPI, BackgroundTasks
import uuid
import logging

from joiner import (
    partition_users,
    partition_transactions,
    join_buckets
)

app = FastAPI()

logging.basicConfig(level=logging.INFO)

jobs = {}


def run_join(job_id):

    logging.info(f"{job_id} started")

    jobs[job_id] = "RUNNING"

    try:

        partition_users()

        partition_transactions()

        join_buckets()

        jobs[job_id] = "COMPLETED"

        logging.info(f"{job_id} completed")

    except Exception as e:

        jobs[job_id] = f"FAILED: {str(e)}"

        logging.error(str(e))


@app.post("/trigger-join")
def trigger_join(
    background_tasks: BackgroundTasks
):

    job_id = str(uuid.uuid4())

    jobs[job_id] = "QUEUED"

    background_tasks.add_task(
        run_join,
        job_id
    )

    return {
        "message": "Join started",
        "job_id": job_id
    }


@app.get("/job-status/{job_id}")
def job_status(job_id: str):

    return {
        "job_id": job_id,
        "status": jobs.get(
            job_id,
            "NOT FOUND"
        )
    }