from app.auth.auth import get_current_username_admin
from app.core import configuration
from typing import Optional
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.routers import auth, gifts, locations, participants, combos, points
from fastapi.responses import JSONResponse

TITLE = configuration.APP_TITLE
VERSION = configuration.APP_VERSION
app = FastAPI(
    title=TITLE,
    version=VERSION,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/docs", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def get_documentation(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(
        openapi_url="/openapi.json", title="Documentation",
    )
    return response


@app.get("/openapi.json", tags=["Documentation"])
async def get_open_api_endpoint(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = JSONResponse(
        get_openapi(title=TITLE, version=VERSION, routes=app.routes)
    )
    return response


@app.get("/redoc", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def redoc_html(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = get_redoc_html(openapi_url="/api/openapi.json", title="Documentation")
    return response


app.include_router(auth.router, prefix="/auth", tags=["Security"])
app.include_router(locations.router, prefix="/location", tags=["Location"])
app.include_router(participants.router, prefix="/participant", tags=["Participant"])
app.include_router(combos.router, prefix="/combo", tags=["Combo"])
app.include_router(gifts.router, prefix="/gift", tags=["Gift"])
app.include_router(points.router, prefix="/point", tags=["Point"])