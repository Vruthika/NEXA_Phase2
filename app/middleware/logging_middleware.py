import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health checks and docs
        if request.url.path in ['/health', '/docs', '/redoc', '/favicon.ico']:
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"Method: {request.method} | "
                f"Path: {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Process Time: {process_time:.4f}s | "
                f"Client: {request.client.host if request.client else 'Unknown'}"
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Process Time: {process_time:.4f}s"
            )
            raise