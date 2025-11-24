import time
from collections import defaultdict
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests: int = 100, window: int = 3600):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.requests_log = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ['/health']:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests
        self.requests_log[client_ip] = [
            req_time for req_time in self.requests_log[client_ip]
            if current_time - req_time < self.window
        ]
        
        # Check rate limit
        if len(self.requests_log[client_ip]) >= self.requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests} requests per {self.window//3600} hour(s)."
            )
        
        # Add current request
        self.requests_log[client_ip].append(current_time)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(self.requests - len(self.requests_log[client_ip]))
        
        return response

# Dependency for per-route rate limiting
class RouteRateLimiter:
    def __init__(self, requests: int = 10, window: int = 60):
        self.requests = requests
        self.window = window
        self.requests_log = defaultdict(list)
    
    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests
        self.requests_log[client_ip] = [
            req_time for req_time in self.requests_log[client_ip]
            if current_time - req_time < self.window
        ]
        
        if len(self.requests_log[client_ip]) >= self.requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests} requests per {self.window} seconds."
            )
        
        self.requests_log[client_ip].append(current_time)
        return True

rate_limiter = RouteRateLimiter(requests=100, window=3600) 
auth_rate_limiter = RouteRateLimiter(requests=5, window=60) 