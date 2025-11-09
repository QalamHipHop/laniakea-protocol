# main.py - Laniakea Protocol Unified Entry Point

import uvicorn
from laniakea.api.main import app
from laniakea.core.config import settings

if __name__ == "__main__":
    from laniakea.utils.logger import logger

logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} API...")
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT,
        log_level="info"
    )
