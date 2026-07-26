"""
Request ID Middleware (Step 8 - Observability)

Adds a unique X-Request-ID header to every response.
This allows ops teams to trace a single request through
logs, databases, and downstream microservices.

In production at Google/Amazon, every log line includes the request ID.
When a customer reports a bug, support can search logs by that ID
and see exactly what happened during that specific request.
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
