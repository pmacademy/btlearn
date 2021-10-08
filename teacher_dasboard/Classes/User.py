from pydantic import BaseSettings
class User(BaseSettings):
    uuid:str
    email:str
    display_name:str