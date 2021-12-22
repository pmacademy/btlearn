import uvicorn
from middlewares.context_set_request_middleware import ContextVarSetRequestMiddleware
from teacher_dashboard.GoogleClassroom import google_classroom
from teacher_dashboard.Students import student
from teacher_dashboard.Classes import classes
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from teacher_dashboard.Assignment.routers import assignment_router_old
from teacher_dashboard.Assignment.routers import assignment_router
from teacher_dashboard.Reporting import reporting_router
from teacher_dashboard.notification import notification_router
from config.app_config import Configurations, get_config
from fastapi import FastAPI
import logging
from config.logs import logging_setup
from middlewares.request_log_middleware import RequestLogMiddleware


logging_setup()

logger = logging.getLogger(__name__)

app = FastAPI()

origins = get_config().ALLOWED_ORIGINS
methods = get_config().ALLOWED_METHODS
headers = get_config().ALLOWED_HEADERS

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origin_regex="(^https\:\/\/.*.bytelearn\.ai$)|(^http\:\/\/localhost\:3000$)",
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(ContextVarSetRequestMiddleware)

app.include_router(assignment_router.router)
app.include_router(assignment_router_old.router)
app.include_router(reporting_router.router)

app.include_router(classes.router)
app.include_router(student.router)
app.include_router(google_classroom.router)

app.include_router(notification_router.router)


@app.get("/")
async def root():
    return {"msg": 'Welcome to classroom api!'}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
