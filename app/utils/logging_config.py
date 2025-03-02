import logging
from app.config.settings import LOG_LEVEL, MONGO_LOG_LEVEL, UVICORN_LOG_LEVEL

def configure_logging():
    """
    Central configuration for all loggers in the application.
    Call this function once at application startup.
    """
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure MongoDB loggers
    mongo_log_level = getattr(logging, MONGO_LOG_LEVEL, logging.WARNING)
    pymongo_logger = logging.getLogger("pymongo")
    pymongo_logger.setLevel(mongo_log_level)
    
    motor_logger = logging.getLogger("motor")
    motor_logger.setLevel(mongo_log_level)
    
    # Configure FastAPI/Uvicorn loggers
    uvicorn_log_level = getattr(logging, UVICORN_LOG_LEVEL, logging.INFO)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(uvicorn_log_level)
    
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(uvicorn_log_level)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - App: {LOG_LEVEL}, MongoDB: {MONGO_LOG_LEVEL}, Uvicorn: {UVICORN_LOG_LEVEL}")