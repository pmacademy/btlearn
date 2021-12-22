from starlette.requests import Request
import logging
import string
import random
import time
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def dispatch(self, request, call_next):
        """logs the request prior to reciving the request 
        and also after sending the response 
        and calculats time taken for the request in the process

        Args:
            request : request recieved 
            call_next : the deault function top be called after that

        Returns:
            response: response recieved after processing the request
        """
        logger = logging.getLogger(__name__)

        logger.debug(f"request_start path=%s", request.url.path)
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)

        logger.debug("request_end completed_in=%s ms status_code=%d",
                     formatted_process_time, response.status_code)

        return response
