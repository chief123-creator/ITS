from typing import Any, Dict
import asyncio

from fastapi import APIRouter, HTTPException, Body

router = APIRouter(prefix="/video", tags=["video"])

# Import service lazily so the route module can be imported even if the service
# is not yet implemented during early development or tests.
try:
    from app.services.video_service import create_video_request  # type: ignore
    _has_video_service = True
except Exception:
    create_video_request = None  # type: ignore
    _has_video_service = False


@router.post("/create-request")
async def create_request(data: Dict[str, Any] = Body(...)):
    """Create a video processing request.

    If the backend video service is not available, return a 501 to indicate
    the feature is not implemented yet.
    """
    if not _has_video_service or create_video_request is None:
        raise HTTPException(status_code=501, detail="video_service.create_video_request not implemented")

    # Call the service; it may be sync or async, handle both.
    result = create_video_request(data)
    if asyncio.iscoroutine(result):
        result = await result
    return result