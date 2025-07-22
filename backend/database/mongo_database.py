"""
MongoDB configuration for unstructured data
Stores detailed analysis results, session data, etc.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio
from backend.utils.config import settings

# MongoDB connection
MONGO_URL = settings.MONGO_URL or "mongodb://localhost:27017"
DATABASE_NAME = "hr_system"

# Async client for FastAPI
async_client = None
async_database = None

# Sync client for non-async operations
sync_client = None
sync_database = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global async_client, async_database
    async_client = AsyncIOMotorClient(MONGO_URL)
    async_database = async_client[DATABASE_NAME]
    
    # Create indexes
    await create_indexes()

async def close_mongo_connection():
    """Close MongoDB connection"""
    global async_client
    if async_client:
        async_client.close()

def get_mongo_client():
    """Get sync MongoDB client"""
    global sync_client, sync_database
    if not sync_client:
        sync_client = MongoClient(MONGO_URL)
        sync_database = sync_client[DATABASE_NAME]
    return sync_client

def get_mongo_db():
    """Get MongoDB database"""
    global async_database
    return async_database

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Resume analyses indexes
        await async_database.resume_analyses.create_index("id")
        await async_database.resume_analyses.create_index("user_id")
        await async_database.resume_analyses.create_index("job_id")
        await async_database.resume_analyses.create_index("analyzed_at")
        
        # Interview sessions indexes
        await async_database.interview_sessions.create_index("id")
        await async_database.interview_sessions.create_index("candidate_id")
        await async_database.interview_sessions.create_index("job_id")
        await async_database.interview_sessions.create_index("started_at")
        
        # Interview messages indexes
        await async_database.interview_messages.create_index("session_id")
        await async_database.interview_messages.create_index("timestamp")
        
        # Call logs indexes
        await async_database.call_logs.create_index("user_id")
        await async_database.call_logs.create_index("initiated_at")
        await async_database.call_logs.create_index("status")
        
        # Onboarding sessions indexes
        await async_database.onboarding_sessions.create_index("id")
        await async_database.onboarding_sessions.create_index("candidate_id")
        await async_database.onboarding_sessions.create_index("started_at")
        
        print("MongoDB indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")
