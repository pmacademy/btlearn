from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from teacher_dasboard.Classes import classes
from teacher_dasboard.Students import student
from teacher_dasboard.GoogleClassroom import google_classroom
import uvicorn
app = FastAPI()
from config.app_config import Configurations,get_config

origins = get_config().ALLOWED_ORIGINS
methods=get_config().ALLOWED_METHODS
headers=get_config().ALLOWED_HEADERS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)

app.include_router(classes.router)
app.include_router(student.router)
app.include_router(google_classroom.router)

@app.get("/")
async def root():
    return Response('Welcome to classroom api!')

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8888, log_level="info")