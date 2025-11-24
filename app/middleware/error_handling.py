import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
            
        except HTTPException as http_exc:
            raise http_exc
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "Validation Error",
                    "message": "Invalid request data",
                    "details": e.errors()
                }
            )
            
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred"
                }
            )