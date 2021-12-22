from logging import Filter, Formatter
import time
import json
from  teacher_dashboard.db_session import context_request


class CustomFilter(Filter):
    def filter(self, record):
        try:
            request = context_request.get()
            record.request_span_id = request.state.request_span_id
        except:
            record.request_span_id = None
        return True


class JsonFormatter:
    ATTR_TO_JSON = ['created', 'filename', 'funcName', 'levelname', 'lineno', 'module', 'msecs',
                    'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'thread', 'threadName']

    def format(self, record):
        obj = {attr: getattr(record, attr)
               for attr in JsonFormatter.ATTR_TO_JSON}
        return json.dumps(obj, indent=4)


class GMTFormatter(Formatter):
    converter = time.gmtime
