
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class GetPasswordReq(BaseModel):
    username: str
    password: str
    site: str


class SetPasswordReq(BaseModel):
    username: str
    password: str
    site: str
    sitepassword: str
