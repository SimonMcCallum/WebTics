"""FastAPI main application for WebTics telemetry backend."""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
import logging

from . import models, schemas, models_research
from .database import engine, get_db
from .routers import research
from .middleware.data_validation import validation_middleware
from .middleware.security import SecurityHeadersMiddleware, https_redirect_middleware

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)
models_research.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebTics Telemetry API",
    description="Lightweight game telemetry and metrics system with research ethics compliance",
    version="0.1.0"
)

# Include research ethics router
app.include_router(research.router)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.middleware("http")(https_redirect_middleware)
app.middleware("http")(validation_middleware)

# CORS middleware - use environment variable for allowed origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them."""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
        }
    )

    # Don't expose internal errors to clients
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."}
    )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "WebTics Telemetry API",
        "version": "0.1.0"
    }


@app.post("/api/v1/sessions", response_model=schemas.MetricSessionResponse)
async def create_session(
    session_data: schemas.MetricSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new metric session."""
    # Check if session already exists
    existing = db.query(models.MetricSession).filter(
        models.MetricSession.unique_id == session_data.unique_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Session already exists")

    db_session = models.MetricSession(
        unique_id=session_data.unique_id,
        build_number=session_data.build_number
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@app.post("/api/v1/sessions/{session_id}/close")
async def close_session(session_id: int, db: Session = Depends(get_db)):
    """Close a metric session."""
    session = db.query(models.MetricSession).filter(
        models.MetricSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.closed_at = datetime.utcnow()
    db.commit()
    return {"status": "closed", "session_id": session_id}


@app.post("/api/v1/play-sessions", response_model=schemas.PlaySessionResponse)
async def create_play_session(
    play_session_data: schemas.PlaySessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new play session within a metric session."""
    # Verify metric session exists
    metric_session = db.query(models.MetricSession).filter(
        models.MetricSession.id == play_session_data.metric_session_id
    ).first()

    if not metric_session:
        raise HTTPException(status_code=404, detail="Metric session not found")

    db_play_session = models.PlaySession(
        metric_session_id=play_session_data.metric_session_id
    )
    db.add(db_play_session)
    db.commit()
    db.refresh(db_play_session)
    return db_play_session


@app.post("/api/v1/play-sessions/{play_session_id}/close")
async def close_play_session(play_session_id: int, db: Session = Depends(get_db)):
    """Close a play session."""
    play_session = db.query(models.PlaySession).filter(
        models.PlaySession.id == play_session_id
    ).first()

    if not play_session:
        raise HTTPException(status_code=404, detail="Play session not found")

    play_session.ended_at = datetime.utcnow()
    db.commit()
    return {"status": "closed", "play_session_id": play_session_id}


@app.post("/api/v1/events", response_model=schemas.EventResponse)
async def log_event(
    event: schemas.EventCreate,
    play_session_id: int,
    db: Session = Depends(get_db)
):
    """Log a single telemetry event."""
    # Verify play session exists
    play_session = db.query(models.PlaySession).filter(
        models.PlaySession.id == play_session_id
    ).first()

    if not play_session:
        raise HTTPException(status_code=404, detail="Play session not found")

    db_event = models.Event(
        play_session_id=play_session_id,
        event_type=event.event_type,
        event_subtype=event.event_subtype,
        x=event.x,
        y=event.y,
        z=event.z,
        magnitude=event.magnitude,
        data=event.data
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.post("/api/v1/events/batch")
async def log_events_batch(
    events: List[schemas.EventCreate],
    play_session_id: int,
    db: Session = Depends(get_db)
):
    """Log multiple telemetry events in a batch."""
    # Verify play session exists
    play_session = db.query(models.PlaySession).filter(
        models.PlaySession.id == play_session_id
    ).first()

    if not play_session:
        raise HTTPException(status_code=404, detail="Play session not found")

    db_events = [
        models.Event(
            play_session_id=play_session_id,
            event_type=event.event_type,
            event_subtype=event.event_subtype,
            x=event.x,
            y=event.y,
            z=event.z,
            magnitude=event.magnitude,
            data=event.data
        )
        for event in events
    ]

    db.add_all(db_events)
    db.commit()

    return {"status": "success", "events_logged": len(db_events)}


@app.get("/api/v1/sessions/{session_id}/events", response_model=List[schemas.EventResponse])
async def get_session_events(
    session_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve events for a specific metric session."""
    # Get all play sessions for this metric session
    play_sessions = db.query(models.PlaySession).filter(
        models.PlaySession.metric_session_id == session_id
    ).all()

    if not play_sessions:
        return []

    play_session_ids = [ps.id for ps in play_sessions]

    events = db.query(models.Event).filter(
        models.Event.play_session_id.in_(play_session_ids)
    ).order_by(models.Event.timestamp.desc()).limit(limit).all()

    return events
