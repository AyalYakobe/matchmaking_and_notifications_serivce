from typing import List, Optional
from fastapi import Response, HTTPException
from openapi_server.models.match import Match
from openapi_server.apis.default_api_base import BaseDefaultApi

# In-memory database substitute
matches_db = {}

class MatchesApiImpl(BaseDefaultApi):
    async def matches_get(self, limit: int, offset: int, donor_id: Optional[str], recipient_id: Optional[str], response: Response) -> List[Match]:
        data = list(matches_db.values())

        # Filters
        if donor_id:
            data = [m for m in data if m.donor_id == donor_id]
        if recipient_id:
            data = [m for m in data if getattr(m, "recipient_id", None) == recipient_id]

        # Pagination
        paginated = data[offset:offset + limit]
        return paginated

    async def matches_post(self, match: Match, response: Response) -> Match:
        match.id = str(len(matches_db) + 1)
        matches_db[match.id] = match
        response.status_code = 201
        response.headers["Location"] = f"/matches/{match.id}"
        return match

    async def matches_id_get(self, id: str) -> Match:
        match = matches_db.get(id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        return match

    async def matches_id_delete(self, id: str) -> None:
        if id not in matches_db:
            raise HTTPException(status_code=404, detail="Match not found")
        del matches_db[id]
        return None
