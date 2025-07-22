"""
Database initialization script
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.sql_database import Base
from backend.models.sql_models import *  # noqa
from backend.models.performance_models import *  # noqa
from backend.models.sql_models import Notification
from backend.utils.config import settings
from backend.models.sql_models import AuditLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by creating all tables"""
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create notifications table
        Notification.__table__.create(bind=engine, checkfirst=True)
        
        # Create audit_logs table
        AuditLog.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("Database tables created successfully!")
        
        # Create a session to verify the connection
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        db.execute("SELECT 1")  # Simple query to test connection
        db.close()
        
        logger.info("Database connection verified successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()
