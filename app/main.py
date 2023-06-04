from app.auth.auth import get_current_username_admin
from app.core import configuration
from typing import Optional
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth,
    control,
    gifts,
    locations,
    meals,
    participants,
    combos,
    points,
    presentations,
    products,
)
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/docs", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def get_documentation(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title="Documentation",
    )
    return response


@app.get("/api/v1/openapi.json", tags=["Documentation"])
async def get_open_api_endpoint(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = JSONResponse(
        get_openapi(title=TITLE, version=VERSION, routes=app.routes)
    )
    return response


@app.get("/api/v1/redoc", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def redoc_html(
    request: Request, user: Optional[dict] = Depends(get_current_username_admin)
):  # This dependency protects our endpoint!
    response = get_redoc_html(openapi_url="/api/v1/openapi.json", title="Documentation")
    return response


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Security"])
app.include_router(locations.router, prefix="/api/v1/location", tags=["Location"])
app.include_router(
    presentations.router, prefix="/api/v1/presentation", tags=["Presentations"]
)
app.include_router(participants.router, prefix="/api/v1/participant", tags=["Participant"])
app.include_router(products.router, prefix="/api/v1/product", tags=["Product"])
app.include_router(combos.router, prefix="/api/v1/combo", tags=["Combo"])
app.include_router(gifts.router, prefix="/api/v1/gift", tags=["Gift"])
app.include_router(control.router, prefix="/api/v1/control", tags=["Control"])
app.include_router(points.router, prefix="/api/v1/points", tags=["Points"])
app.include_router(meals.router, prefix="/api/v1/meals", tags=["Meals"])
