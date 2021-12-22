import sys
from functools import lru_cache
import logging
import logging.config
import yaml
import json
import sys
import inspect


def logging_setup():
    with open('./config/log_config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


# def log(orig_func):
#     def decorator(*args, **kwargs):
#         print("Decorating wrapper called for method %s" % orig_func.__name__)
#         result = orig_func(*args, **kwargs)
#         return result
#     return decorator


# def log_decorator(obj):
#     if(inspect.isclass(obj)):
#         for name, method in inspect.getmembers(obj):
#             if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
#                 continue
#             setattr(obj, name, log_decorator(method))
#         return obj
#     elif(inspect.isfunction(obj) or inspect.ismethod(obj)):
#         def decorator(*args, **kwargs):
#             logger = logging.getLogger(__name__)
#             logger.debug("Calling method %s" %
#                          obj.__name__)
#             result = obj(*args, **kwargs)
#             return result
#         return decorator
