#SQLAlchemy database models
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class EndpointStatusDB(Base):
    #Endpoint status database model
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
    #Alert database model
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
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/monitoring"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    #Get database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    #Initialize database tables
    Base.metadata.create_all(bind=engine)