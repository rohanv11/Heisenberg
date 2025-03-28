from app.config.backend import DatabaseManager
from app.config.settings import DEBUG_MODE
from app.utils.misc import setup_debugger

async def startup_db_client():
    await DatabaseManager.connect_to_mongo()

async def setup_debug_if_enabled():
    if DEBUG_MODE:
        print("DEBUG_MODE is True")
        setup_debugger()

async def shutdown_db_client():
    await DatabaseManager.close_mongo_connection()
