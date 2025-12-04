"""
Request ID Middleware
Adds a unique request ID to every HTTP request for distributed tracing and logging.
Features:
- Supports client-provided request IDs via X-Request-ID header
- Auto-generates UUID if no ID is provided
- Stores request ID in request.state for route access
- Adds request ID to response headers
- Logs request start, completion, and errors with timing
- Includes request ID in all log messages via logging filter
Usage:
    app.add_middleware(RequestIDMiddleware)
"""

import uuid
import logging
import time
from contextvars import ContextVar
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure logging
logger = logging.getLogger(__name__)
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to every HTTP request.
    The request ID is:
    - Stored in request.state.request_id
    - Added to all log messages via RequestIDFilter
    - Returned in response header X-Request-ID
    - Used for tracing requests across services
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Process request and inject request ID.
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
        Returns:
            HTTP response with X-Request-ID and X-Response-Time headers
        """
        # Get or generate request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.state.request_id = request_id

        # Set request ID in context for logging
        request_id_var.set(request_id)

        # Log request start
        start_time = time.time()
        logger.info(
            f"[{request_id}] → {request.method} {request.url.path} "
            f"(client: {request.client.host if request.client else 'unknown'})"
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log completion
            logger.info(
                f"[{request_id}] ← {request.method} {request.url.path} "
                f"- {response.status_code} ({duration_ms}ms)"
            )

            # Add headers
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Response-Time'] = f"{duration_ms}ms"

            return response

        except Exception as e:
            # Log errors
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"[{request_id}] ✗ {request.method} {request.url.path} "
                f"- ERROR: {str(e)} ({duration_ms}ms)"
            )
            raise

        finally:
            # Clean up context
            request_id_var.set(None)

class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds request ID to all log records.
    Automatically extracts request ID from context.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id to log record.
        Args:
            record: Log record to modify
        Returns:
            True (always allow the log record)
        """
        record.request_id = request_id_var.get() or '-'
        return True

def get_request_id(request: Request) -> str:
    """
    Get request ID from current request.
    Args:
        request: FastAPI/Starlette request object
    Returns:
        Request ID string or 'unknown' if not found
    """
    try:
        return request.state.request_id
    except AttributeError:
        return 'unknown'
