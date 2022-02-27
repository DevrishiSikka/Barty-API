from pydantic import BaseModel

class AuthDetail(BaseModel):
    username: str
    password: str

