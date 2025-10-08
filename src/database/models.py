# SQLAlchemy database models
import os
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class EndpointStatusDB(Base):
    # Endpoint status database model
    __tablename__ = "endpoint_status"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_name = Column(String(255), nullable=False, index=True)
    url = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    ssl_valid = Column(Boolean, nullable=True)
    ssl_expires = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    uptime_percentage = Column(Float, nullable=True)


class AlertDB(Base):
    # Alert database model
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_name = Column(String(255), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)


# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/monitoring"
)

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create engine (only if not in test mode)
TESTING = os.getenv("TESTING", "false").lower() == "true"

if not TESTING:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        engine = None
        SessionLocal = None
else:
    # Use SQLite in-memory for tests
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    # Get database session
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Initialize database tables
    if engine is not None:
        Base.metadata.create_all(bind=engine)
