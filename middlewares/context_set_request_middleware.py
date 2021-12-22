from starlette.requests import Request
import logging
import string
import random
import time
from starlette.middleware.base import BaseHTTPMiddleware
from teacher_dashboard.db_session import context_request


class ContextVarSetRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def dispatch(self, request, call_next):
        """adds request id to each request so that the request can be tracked

        Args:
            request : request recieved 
            call_next : the deault function top be called after that

        Returns:
            response: response recieved after processing the request
        """

        span_id = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=10))
        request.state.request_span_id = span_id

        context_request.set(request)

        response = await call_next(request)

        return response
