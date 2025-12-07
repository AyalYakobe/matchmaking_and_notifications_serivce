from fastapi import APIRouter, HTTPException, Response, BackgroundTasks
from typing import List
import uuid
import time

from openapi_server.models.match import Match, MatchCreate, MatchUpdate
from openapi_server.services.matcher_service import (
    list_matches,
    create_match,
    get_match,
    update_match,
    delete_match,
    get_full_match,
)

# NEW async task service
from openapi_server.services.async_tasks_service import (
    create_async_task,
    update_async_task,
    get_async_task,
)

router = APIRouter()


# ===============================================================
# BACKGROUND WORKER (runs async tasks)
# ===============================================================
def simulate_long_match_process(task_id: str, match_id: int):
    """
    Simulates a long-running workload (5 seconds).
    When complete, updates task row in DB.
    """
    time.sleep(5)

    update_async_task(
        task_id,
        "completed",
        {
            "message": f"Async processing complete for match {match_id}",
            "match_id": match_id,
        },
    )


# ===============================================================
# GET /matches — list all matches + basic pagination
# ===============================================================
@router.get("/matches", response_model=List[Match], tags=["Matches"])
def route_list_matches(limit: int = 25, offset: int = 0, response: Response = None):
    rows = list_matches()

    # Manual slice
    sliced = rows[offset : offset + limit]

    # Pagination Link header
    next_offset = offset + limit
    if next_offset < len(rows):
        response.headers["Link"] = (
            f'</matches?limit={limit}&offset={next_offset}>; rel="next"'
        )
    else:
        response.headers["Link"] = ""

    return sliced


# ===============================================================
# POST /matches — create (201)
# ===============================================================
@router.post("/matches", response_model=Match, status_code=201, tags=["Matches"])
def route_create_match(payload: MatchCreate, response: Response):
    new_match = create_match(payload)

    match_id = new_match["id"]

    # REST: include Location
    response.headers["Location"] = f"/matches/{match_id}"
    response.headers["Content-Location"] = f"/matches/{match_id}"

    return new_match


# ===============================================================
# GET /matches/{match_id}
# ===============================================================
@router.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_get_match(match_id: int):
    match = get_match(match_id)
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")
    return match


# ===============================================================
# PUT/PATCH /matches/{match_id}
# ===============================================================
@router.patch("/matches/{match_id}", response_model=Match, tags=["Matches"])
@router.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_update_match(match_id: int, payload: MatchUpdate):
    updated = update_match(match_id, payload)
    if updated is None:
        raise HTTPException(404, f"Match {match_id} not found")
    return updated


# ===============================================================
# DELETE /matches/{match_id}
# ===============================================================
@router.delete("/matches/{match_id}", status_code=204, tags=["Matches"])
def route_delete_match(match_id: int):
    ok = delete_match(match_id)
    if not ok:
        raise HTTPException(404, f"Match {match_id} not found")
    return


# ===============================================================
# GET /matches/{match_id}/full
# ===============================================================
@router.get("/matches/{match_id}/full", tags=["Matches"])
def route_get_full_match(match_id: int):
    result = get_full_match(match_id)
    if result is None:
        raise HTTPException(404, f"Match {match_id} not found")
    return result


# ===============================================================
# POST /matches/{match_id}/async — 202 Accepted (DB-backed)
# ===============================================================
@router.post("/matches/{match_id}/async", status_code=202, tags=["Matches"])
def route_async_process_match(
    match_id: int,
    background: BackgroundTasks,
    response: Response,
):
    match = get_match(match_id)
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")

    # Create new task ID
    task_id = str(uuid.uuid4())

    # Insert into DB
    create_async_task(task_id, match_id)

    # Run background process
    background.add_task(simulate_long_match_process, task_id, match_id)

    # REST 202 headers
    response.headers["Location"] = f"/matches/async/tasks/{task_id}"
    response.headers["Retry-After"] = "3"

    return {"task_id": task_id, "status": "running"}


# ===============================================================
# GET /matches/async/tasks/{task_id}
# ===============================================================
@router.get("/matches/async/tasks/{task_id}", tags=["Matches"])
def route_async_task_status(task_id: str):
    task = get_async_task(task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    return task
