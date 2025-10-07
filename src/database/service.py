#Database service for storing monitoring data
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from src.database.models import EndpointStatusDB, AlertDB
from src.models.status_models import EndpointStatus

logger = logging.getLogger(__name__)


class DatabaseService:
    #Service for database operations

    def __init__(self, db: Session):
        self.db = db

    def save_endpoint_status(self, status: EndpointStatus) -> bool:
        #Save endpoint status to database
        try:
            db_status = EndpointStatusDB(
                endpoint_name=status.name,
                url=status.url,
                status=status.status.value,
                status_code=status.status_code,
                response_time=status.response_time,
                ssl_valid=status.ssl_valid,
                ssl_expires=status.ssl_expires,
                error_message=status.error,
                timestamp=status.timestamp,
                uptime_percentage=status.uptime_percentage
            )
            self.db.add(db_status)
            self.db.commit()
            logger.info(f"Saved status for {status.name}")
            return True
        except Exception as e:
            logger.error(f"Error saving status: {e}")
            self.db.rollback()
            return False

    def save_alert(self, alert_data: Dict[str, Any]) -> bool:
        #Save alert to database
        try:
            db_alert = AlertDB(
                endpoint_name=alert_data.get("endpoint"),
                alert_type=alert_data.get("type"),
                message=str(alert_data),
                severity=self._get_severity(alert_data.get("type")),
                created_at=datetime.fromisoformat(
                    alert_data.get("timestamp")
                )
            )
            self.db.add(db_alert)
            self.db.commit()
            logger.info(
                f"Saved alert for {alert_data.get('endpoint')}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            self.db.rollback()
            return False

    def get_endpoint_history(
        self, 
        endpoint_name: str, 
        hours: int = 24
    ) -> List[EndpointStatusDB]:
        #Get endpoint status history
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return self.db.query(EndpointStatusDB).filter(
                and_(
                    EndpointStatusDB.endpoint_name == endpoint_name,
                    EndpointStatusDB.timestamp >= cutoff_time
                )
            ).order_by(EndpointStatusDB.timestamp.desc()).all()
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

    def get_all_endpoints_history(
        self, 
        hours: int = 24
    ) -> List[EndpointStatusDB]:
        #Get history for all endpoints
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return self.db.query(EndpointStatusDB).filter(
                EndpointStatusDB.timestamp >= cutoff_time
            ).order_by(EndpointStatusDB.timestamp.desc()).all()
        except Exception as e:
            logger.error(f"Error getting all history: {e}")
            return []

    def get_recent_alerts(
        self, 
        endpoint_name: Optional[str] = None, 
        limit: int = 50
    ) -> List[AlertDB]:
        #Get recent alerts
        try:
            query = self.db.query(AlertDB)
            if endpoint_name:
                query = query.filter(
                    AlertDB.endpoint_name == endpoint_name
                )
            return query.order_by(
                AlertDB.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def calculate_uptime(
        self, 
        endpoint_name: str, 
        hours: int = 24
    ) -> float:
        #Calculate uptime percentage from database
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            total = self.db.query(EndpointStatusDB).filter(
                and_(
                    EndpointStatusDB.endpoint_name == endpoint_name,
                    EndpointStatusDB.timestamp >= cutoff_time
                )
            ).count()
            
            if total == 0:
                return 100.0
            
            healthy = self.db.query(EndpointStatusDB).filter(
                and_(
                    EndpointStatusDB.endpoint_name == endpoint_name,
                    EndpointStatusDB.timestamp >= cutoff_time,
                    EndpointStatusDB.status == "healthy"
                )
            ).count()
            
            return round((healthy / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating uptime: {e}")
            return 0.0

    def cleanup_old_data(self, days: int = 30) -> int:
        #Delete data older than specified days
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Delete old status records
            deleted_status = self.db.query(EndpointStatusDB).filter(
                EndpointStatusDB.timestamp < cutoff_time
            ).delete()
            
            # Delete old alerts
            deleted_alerts = self.db.query(AlertDB).filter(
                AlertDB.created_at < cutoff_time
            ).delete()
            
            self.db.commit()
            
            total_deleted = deleted_status + deleted_alerts
            logger.info(
                f"Cleaned up {total_deleted} old records "
                f"(status: {deleted_status}, alerts: {deleted_alerts})"
            )
            return total_deleted
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            self.db.rollback()
            return 0

    @staticmethod
    def _get_severity(alert_type: str) -> str:
        #Determine alert severity based on type
        severity_map = {
            "downtime": "critical",
            "timeout": "high",
            "slow_response": "medium",
            "ssl_expiry": "high",
            "recovery": "info"
        }
        return severity_map.get(alert_type, "medium")