"""
Точка входа приложения
"""

import uvicorn

from src.app.setup.config.settings import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.app.setup.app_factory:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True,
    )
