"""Server-rendered student/instructor portal pages.

These are thin Jinja2 shells; the in-page JavaScript talks to the JSON API using a JWT
held in localStorage. Markdown docs are rendered to HTML on the ``/app/docs`` page.
"""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .. import config

router = APIRouter(prefix="/app", tags=["portal"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _ctx(request: Request, **extra):
    base = {
        "request": request,
        "student_brand": config.STUDENT_BRAND,
        "service_brand": config.SERVICE_BRAND,
        "public_base_url": config.PUBLIC_BASE_URL,
    }
    base.update(extra)
    return base


@router.get("/", response_class=HTMLResponse)
@router.get("", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", _ctx(request))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", _ctx(request))


@router.get("/claim", response_class=HTMLResponse)
async def claim_page(request: Request):
    return templates.TemplateResponse("claim.html", _ctx(request))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", _ctx(request))


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", _ctx(request))


@router.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Render the self-contained quickstart bundled in the template."""
    return templates.TemplateResponse("docs.html", _ctx(request))
