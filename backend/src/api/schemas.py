from pydantic import BaseModel


class AddUser(BaseModel):
    id: str
    email: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str


class AddReport(BaseModel):
    title: str
    content: str
