"""FastAPI application initialization and configuration."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from pathlib import Path

from app.config import settings
from app.database import create_db_and_tables, run_migrations
from app.api import runs
from app.api import projects as projects_api
from app.api import features as features_api
from app.web import routes as web_routes, htmx_routes, project_routes
from app.services.exceptions import (
    RunNotFoundError,
    CaseNotFoundError,
    InvalidStateError,
    FileUploadError,
    ValidationError,
    ProjectNotFoundError,
    EpicNotFoundError,
    FeatureNotFoundError,
    TestCaseDefinitionNotFoundError,
    DeletionConstraintError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="RedstoneReporter",
    description="AI Agent Test Reporter - Custom Monocart Alternative",
    version="0.1.0",
)


# Exception handlers for custom errors
@app.exception_handler(RunNotFoundError)
async def run_not_found_handler(request: Request, exc: RunNotFoundError):
    """Handle RunNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "RUN_NOT_FOUND",
            "run_id": exc.run_id
        }
    )


@app.exception_handler(CaseNotFoundError)
async def case_not_found_handler(request: Request, exc: CaseNotFoundError):
    """Handle CaseNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "CASE_NOT_FOUND",
            "case_id": exc.case_id
        }
    )


@app.exception_handler(InvalidStateError)
async def invalid_state_handler(request: Request, exc: InvalidStateError):
    """Handle InvalidStateError with 400 response."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_code": "INVALID_STATE"
        }
    )


@app.exception_handler(FileUploadError)
async def file_upload_error_handler(request: Request, exc: FileUploadError):
    """Handle FileUploadError with 500 response."""
    logger.error(f"File upload error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "error_code": "FILE_UPLOAD_ERROR"
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle ValidationError with 400 response."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_code": "VALIDATION_ERROR"
        }
    )


@app.exception_handler(ProjectNotFoundError)
async def project_not_found_handler(request: Request, exc: ProjectNotFoundError):
    """Handle ProjectNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "PROJECT_NOT_FOUND",
            "project_id": exc.project_id
        }
    )


@app.exception_handler(EpicNotFoundError)
async def epic_not_found_handler(request: Request, exc: EpicNotFoundError):
    """Handle EpicNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "EPIC_NOT_FOUND",
            "epic_id": exc.epic_id
        }
    )


@app.exception_handler(FeatureNotFoundError)
async def feature_not_found_handler(request: Request, exc: FeatureNotFoundError):
    """Handle FeatureNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "FEATURE_NOT_FOUND",
            "feature_id": exc.feature_id
        }
    )


@app.exception_handler(TestCaseDefinitionNotFoundError)
async def definition_not_found_handler(request: Request, exc: TestCaseDefinitionNotFoundError):
    """Handle TestCaseDefinitionNotFoundError with 404 response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "DEFINITION_NOT_FOUND",
            "definition_id": exc.definition_id
        }
    )


@app.exception_handler(DeletionConstraintError)
async def deletion_constraint_handler(request: Request, exc: DeletionConstraintError):
    """Handle DeletionConstraintError with 409 response."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
            "error_code": "DELETION_CONSTRAINT",
            "resource_type": exc.resource_type,
            "resource_id": exc.resource_id
        }
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with formatted response."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_code": "REQUEST_VALIDATION_ERROR"
        }
    )


@app.on_event("startup")
async def on_startup():
    """Initialize database and perform startup checks."""
    logger.info("Starting RedstoneReporter...")

    # Create database tables if they don't exist (NFR-04)
    create_db_and_tables()
    logger.info("Database initialized successfully")

    # Run migrations for adding new columns to existing tables (NFR-07)
    run_migrations()
    logger.info("Database migrations completed")

    # Verify screenshot directory exists
    if settings.SCREENSHOT_DIR.exists():
        logger.info(f"Screenshot directory: {settings.SCREENSHOT_DIR}")
    else:
        logger.warning(f"Screenshot directory not found: {settings.SCREENSHOT_DIR}")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "RedstoneReporter",
        "version": "0.1.0"
    }


# Include API routers
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
logger.info("API routes mounted at /api/runs")

app.include_router(projects_api.router, prefix="/api", tags=["projects"])
logger.info("Projects API routes mounted at /api")

app.include_router(features_api.router, prefix="/api", tags=["features"])
logger.info("Features API routes mounted at /api")

# Include Web UI routers
app.include_router(web_routes.router, tags=["web"])
logger.info("Web routes mounted")

app.include_router(project_routes.router, tags=["web-projects"])
logger.info("Project web routes mounted")

# Include HTMX partial routers
app.include_router(htmx_routes.router, prefix="/api/htmx", tags=["htmx"])
logger.info("HTMX routes mounted at /api/htmx")


# Mount static files (will be used for CSS/JS)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted at /static")

# Mount screenshots directory for serving images
if settings.SCREENSHOT_DIR.exists():
    app.mount(
        "/screenshots",
        StaticFiles(directory=str(settings.SCREENSHOT_DIR)),
        name="screenshots"
    )
    logger.info("Screenshots mounted at /screenshots")

# Setup Jinja2 templates
templates_dir = Path("app/templates")
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    logger.info(f"Jinja2 templates configured: {templates_dir}")
else:
    # Templates will be created in later phases
    templates = None
    logger.warning("Templates directory not found (will be created in later phases)")
