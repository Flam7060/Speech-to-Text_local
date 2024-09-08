# app/routers/frontend_router.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("frontend/index.html")


@router.get("/choice-voice", response_class=HTMLResponse)
async def read_choice_voice():
    return FileResponse("frontend/pages/choice-voice.html")


@router.get("/test", response_class=HTMLResponse)
async def read_test():
    return FileResponse("frontend/pages/test.html")
