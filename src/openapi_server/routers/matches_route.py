# src/openapi_server/routers/matches_route.py

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

router = APIRouter()

# ===============================================================
# OPTIONAL: In-memory async-task store (for 202 Accepted example)
# ===============================================================
ASYNC_TASKS = {}


def simulate_long_match_process(task_id: str, match_id: str):
    """Simulate a long running async operation."""
    time.sleep(5)
    ASYNC_TASKS[task_id]["status"] = "completed"
    ASYNC_TASKS[task_id]["result"] = {
        "message": f"Async processing complete for match {match_id}",
        "match_id": match_id,
    }


# ===============================================================
# GET /matches - list + pagination Link header
# ===============================================================
@router.get("/matches", response_model=List[Match], tags=["Matches"])
def route_list_matches(limit: int = 25, offset: int = 0, response: Response = None):
    data = list_matches()

    # Pagination: slice manually
    sliced = data[offset : offset + limit]

    # Build pagination Link header (relative URLs)
    next_offset = offset + limit
    if next_offset < len(data):
        response.headers["Link"] = (
            f'</matches?limit={limit}&offset={next_offset}>; rel="next"'
        )
    else:
        response.headers["Link"] = ""

    return sliced


# ===============================================================
# POST /matches - create (201 + Location header)
# ===============================================================
@router.post("/matches", response_model=Match, status_code=201, tags=["Matches"])
def route_create_match(payload: MatchCreate, response: Response):
    new_match = create_match(payload)

    # Add REST Location header
    response.headers["Location"] = f"/matches/{new_match.id}"

    return new_match


# ===============================================================
# GET /matches/{match_id} - retrieve
# ===============================================================
@router.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_get_match(match_id: str):
    match = get_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match


# ===============================================================
# PUT/PATCH /matches/{match_id} - update
# ===============================================================
@router.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
@router.patch("/matches/{match_id}", response_model=Match, tags=["Matches"])
def route_update_match(match_id: str, payload: MatchUpdate):
    updated = update_match(match_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return updated


# ===============================================================
# DELETE /matches/{match_id}
# ===============================================================
@router.delete("/matches/{match_id}", status_code=204, tags=["Matches"])
def route_delete_match(match_id: str):
    ok = delete_match(match_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return


# ===============================================================
# GET /matches/{match_id}/full
# ===============================================================
@router.get("/matches/{match_id}/full", tags=["Matches"])
def route_get_full_match(match_id: str):
    result = get_full_match(match_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return result


# ===============================================================
# POST /matches/{match_id}/async — 202 ACCEPTED example
# ===============================================================
@router.post("/matches/{match_id}/async", status_code=202, tags=["Matches"])
def route_async_process_match(
    match_id: str,
    background: BackgroundTasks,
    response: Response
):
    if get_match(match_id) is None:
        raise HTTPException(404, f"Match {match_id} not found")

    # Create task ID
    task_id = str(uuid.uuid4())

    # Store initial task state
    ASYNC_TASKS[task_id] = {
        "task_id": task_id,
        "status": "running",
        "result": None,
    }

    # Run background processing
    background.add_task(simulate_long_match_process, task_id, match_id)

    # Include Location header for polling the task
    response.headers["Location"] = f"/matches/async/tasks/{task_id}"
    response.headers["Retry-After"] = "3"

    return {"task_id": task_id, "status": "accepted"}


# ===============================================================
# GET /matches/async/tasks/{task_id} — poll async task
# ===============================================================
@router.get("/matches/async/tasks/{task_id}", tags=["Matches"])
def route_async_task_status(task_id: str):
    task = ASYNC_TASKS.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task
